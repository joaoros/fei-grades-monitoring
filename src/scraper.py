"""
Scraper for extracting grades from the Interage FEI portal.
"""
import os
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class InterageScraper:
    """Class responsible for authenticating and extracting grades from the Interage portal."""
    def __init__(self, user: str, password: str):
        logger.info("Initializing InterageScraper.")
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.url_login = "https://interage.fei.org.br/secureserver/portal/"
        self.url_grades = "https://interage.fei.org.br/secureserver/portal/graduacao/secretaria/consultas/notas"

    def login(self) -> None:
        """Logs in to the Interage portal."""
        logger.info("Logging in to Interage.")
        res = self.session.get(self.url_login)
        res.raise_for_status()
        token = self._get_verification_token(res.text)
        payload = {
            "__RequestVerificationToken": token,
            "Usuario": self.user,
            "Senha": self.password
        }
        res_post = self.session.post(self.url_login, data=payload)
        res_post.raise_for_status()
        if "Usuário ou senha inválidos" in res_post.text:
            logger.error("Invalid username or password.")
            raise RuntimeError("Invalid username or password.")
        logger.info("Login successful.")

    def acessar_pagina_notas(self) -> str:
        """Accesses the grades page after login."""
        logger.info("Accessing grades page.")
        res = self.session.get(self.url_grades)
        res.raise_for_status()
        if "Sessão expirada" in res.text or "login" in res.url:
            logger.error("Session expired or not authenticated.")
            raise RuntimeError("Session expired or not authenticated.")
        logger.info("Grades page accessed successfully.")
        return res.text

    def extrair_notas(self, html: str) -> List[Dict[str, Any]]:
        """Extracts grades from the grades page HTML."""
        logger.info("Extracting grades from HTML.")
        soup = BeautifulSoup(html, "html.parser")
        header_block = self._find_grades_header_block(soup)
        if not header_block:
            logger.error("Grades header block not found.")
            raise RuntimeError("Grades header block not found.")
        content_block = header_block.find_next_sibling("div", class_="bloco-conteudo-intermediario")
        if not content_block:
            logger.error("Intermediate grades block not found.")
            raise RuntimeError("Intermediate grades block not found.")
        panels = content_block.find_all("div", class_="panel panel-default")
        if not panels:
            logger.error("No grade panels found.")
            raise RuntimeError("No grade panels found.")
        result = []
        for panel in panels:
            header = panel.find("h4", class_="panel-title")
            if not header:
                continue
            name = self._extract_subject_name(header)
            if not name:
                continue
            table = panel.find("table")
            grades, average = self._extract_table_data(table)
            result.append({
                "nome": name,
                "notas": grades,
                "media": average
            })
        logger.info(f"Extracted grades: {result}")
        return result

    @staticmethod
    def _get_verification_token(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        token_tag = soup.find("input", {"name": "__RequestVerificationToken"})
        if not token_tag:
            logger.error("Verification token not found on login page.")
            raise RuntimeError("Verification token not found.")
        return token_tag["value"]

    @staticmethod
    def _find_grades_header_block(soup: BeautifulSoup):
        for div in soup.find_all("div", class_="bloco-conteudo-cabecalho"):
            h4 = div.find("h4")
            if h4 and "Notas (Semestre Atual)" in h4.get_text():
                return div
        return None

    @staticmethod
    def _extract_subject_name(header) -> str:
        a = header.find("a", class_="tabela-notas")
        if not a:
            return None
        parts = a.get_text(separator=" ").strip().split("-")
        return parts[1].strip() if len(parts) >= 2 else None

    @staticmethod
    def _extract_table_data(table) -> (Dict[str, Any], Any):
        grades = {}
        average = None
        rows = table.find("tbody").find_all("tr") if table and table.find("tbody") else []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            key = cols[0].get_text(strip=True)
            value = cols[1].get_text(strip=True).replace(",", ".") if cols[1].get_text(strip=True) else None
            if "Média" in key or "Final" in key:
                average = value
            elif key:
                grades[key] = value
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            key = cols[0].get_text(strip=True)
            if key and key not in grades and not ("Média" in key or "Final" in key):
                grades[key] = None
        return grades, average