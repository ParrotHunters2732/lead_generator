from random import uniform
from time import sleep
from scraper.yellowpages import YellowPagesScraper
from database.supabase import Writer
from logs.log import CustomLogger

logger = CustomLogger().get_logger(__name__)

def retry_on_fail_page(error_list: list, self, unit: str, execute, write_success):
    if not self.redo_on_fail_page or not error_list:
        logger.info(f"{unit} retry skipped: redo_on_fail_page={self.redo_on_fail_page} error_list={error_list}")
        return []
    remaining = list(error_list)
    for attempt_number in range(1, self.redo_on_fail_page_attempt + 1):
        logger.info(f"{unit} retry attempt {attempt_number}/{self.redo_on_fail_page_attempt} remaining={len(remaining)}")
        still_failed = []
        for item in remaining:
            pick_float = uniform(self.rate_min, self.rate_max)
            logger.info(f"{unit} retry waiting {pick_float:.1f}s")
            sleep(pick_float)
            result = execute(item)
            if result:
                write_success(result, item)
            else:
                logger.info(f"{unit} retry failed for {item}")
                still_failed.append(item)
        if not still_failed:
            return []
        remaining = still_failed
        sleep(self.attempt_duration)
    return remaining

def retry_business_list_fail_pages(error_list: list, self, category, location, session):
    def execute(page):
        result = YellowPagesScraper().get_business_list(
            category=category,
            location=location,
            page=page,
            session=session,
            attempt= self.max_attempt,
        )
        if result == 404:
            logger.error("There is no data about this page")
            return True
        return result
    def write_success(result, page):
        Writer().write_business_list(business_list_data=result) 
    return retry_on_fail_page(error_list, self, "business_list", execute, write_success)


def retry_business_insight_fail_pages(error_list: list, self, session,db_writer: Writer):
    def execute(item):
        num, url_unq = item
        return YellowPagesScraper().get_business_insight(
            target_url=url_unq[0],
            session=session,
            attempt=self.max_attempt,
        )

    def write_success(result, item):
        _, url_unq = item
        db_writer.write_business_insight(dict_business_insight=result, unique_key=url_unq[1])

    return retry_on_fail_page(error_list, self, "business_insight", execute, write_success)