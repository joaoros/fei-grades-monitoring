    """
    Main Lambda function for grade monitoring.
    """
    import os
    import json
    import logging
    from scraper import InterageScraper
    from db import store_changed_grades, get_all_grades
    from notifier import notify_grade_difference

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    def _get_credentials():
        """Gets credentials from environment."""
        user = os.environ("PORTAL_USERNAME")
        password = os.environ("PORTAL_PASSWORD")
        if not user or not password:
            logger.error("Credentials not set in environment.")
            raise ValueError("Credentials not set in environment.")
        return user, password

    def _process_grades(user: str, password: str) -> None:
        """Runs the login, extraction, and notification flow for grades."""
        scraper = InterageScraper(user, password)
        scraper.login()
        html_grades = scraper.acessar_pagina_notas()
        grades = scraper.extrair_notas(html_grades)
        previous_grades = get_all_grades()
        changed = store_changed_grades(grades, previous_grades)
        if changed:
            logger.info("Changed grades detected. Notifying user.")
            notify_grade_difference(previous_grades, grades)
        else:
            logger.info("No grade changes detected.")

    def lambda_handler(event, context):
        """Main AWS Lambda handler."""
        logger.info("Lambda handler started.")
        try:
            user, password = _get_credentials()
            _process_grades(user, password)
            return {
                "statusCode": 200,
                "body": json.dumps("Grades processed successfully.")
            }
        except ValueError as ve:
            return {
                "statusCode": 400,
                "body": json.dumps(str(ve))
            }
        except Exception as e:
            logger.exception("Error during Lambda execution.")
            return {
                "statusCode": 500,
                "body": json.dumps(f"Error: {str(e)}")
            }