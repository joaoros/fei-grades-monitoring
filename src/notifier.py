"""
Email notification module for grade changes.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def send_email_notification(subject: str, body: str, html_body: Optional[str] = None) -> None:
    """Sends an email notification."""
    email_sender = os.environ["EMAIL_SENDER"]
    email_receiver = os.environ["EMAIL_RECEIVER"]
    password = os.environ["EMAIL_PASSWORD"]

    logger.info(f"Preparing to send email from {email_sender} to {email_receiver} with subject '{subject}'")
    msg = MIMEMultipart('alternative')
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_sender, password)
            server.send_message(msg)
        logger.info("Email sent successfully.")
    except Exception as e:
        logger.exception(f"Failed to send email: {e}")

def _grades_to_html_rows(grades: Optional[Dict[str, Any]]) -> str:
    if not grades:
        return ''
    return ''.join(
        f'<tr><td style="padding:4px 8px;">{k}</td><td style="padding:4px 8px;">{v if v is not None else "-"}</td></tr>'
        for k, v in grades.items()
    )

def format_grades_table(name: str, old: Optional[Dict[str, Any]], new: Dict[str, Any]) -> str:
    """Formats the HTML table for grade comparison."""
    old_grades = old['notas'] if old else None
    new_grades = new['notas']
    old_average = old['media'] if old else 'N/A'
    new_average = new['media']
    return f'''
    <h3 style="margin-bottom:2px;">{name}</h3>
    <table border="1" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-bottom:10px;">
      <tr><th style="padding:4px 8px;background:#f0f0f0;">Previous Grades</th><th style="padding:4px 8px;background:#f0f0f0;">Current Grades</th></tr>
      <tr>
        <td valign="top"><table>{_grades_to_html_rows(old_grades)}</table></td>
        <td valign="top"><table>{_grades_to_html_rows(new_grades)}</table></td>
      </tr>
      <tr><td style="padding:4px 8px;">Previous Average: <b>{old_average if old_average is not None else 'N/A'}</b></td><td style="padding:4px 8px;">Current Average: <b>{new_average if new_average is not None else 'N/A'}</b></td></tr>
    </table>
    '''

def _get_grade_changes(old_grades: List[Dict[str, Any]], new_grades: List[Dict[str, Any]]) -> List[Tuple[str, Optional[Dict[str, Any]], Dict[str, Any]]]:
    """Returns a list of tuples (name, old, new) for changed subjects."""
    old_dict = {g['nome']: g for g in old_grades}
    new_dict = {g['nome']: g for g in new_grades}
    return [
        (name, old_dict.get(name), new_grade)
        for name, new_grade in new_dict.items()
        if old_dict.get(name) != new_grade
    ]

def notify_grade_difference(old_grades: List[Dict[str, Any]], new_grades: List[Dict[str, Any]]) -> None:
    """Notifies by email if there is a grade difference."""
    changes = _get_grade_changes(old_grades, new_grades)
    if not changes:
        logger.info("No grade difference detected. No email sent.")
        return

    logger.info("Grade difference detected. Sending email notification.")
    if len(changes) == 1:
        subject = f"Grade update: {changes[0][0]}"
    else:
        names = ', '.join([name for name, _, _ in changes])
        subject = f"Grade updates: {names}"

    body = "The following grades have changed:\n"
    html_body = "<html><body><h3>Hello! 😃 The following grades have changed:</h3><hr>"
    for name, old, new in changes:
        body += f"\nSubject: {name}\nPrevious grades: {old['notas'] if old else 'N/A'}\nCurrent grades:    {new['notas']}\nPrevious average: {old['media'] if old else 'N/A'}\nCurrent average:    {new['media']}\n"
        html_body += format_grades_table(name, old, new)
    html_body += "</body></html>"
    send_email_notification(subject, body, html_body)