import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from etl.collectors.vessel_position import collect_vessel_positions
from etl.collectors.vessel_event import collect_vessel_events
from etl.collectors.berth_facility import collect_berth_facilities
from etl.collectors.berth_status import collect_berth_status
from etl.collectors.weather import collect_weather
from etl.collectors.statistics import collect_statistics
from etl.collectors.route_gis import collect_route_gis
from etl.collectors.tank_terminal import collect_tank_terminals

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(collect_vessel_positions, "interval", minutes=1, id="vessel_positions")
    scheduler.add_job(collect_vessel_events, "interval", minutes=5, id="vessel_events")
    scheduler.add_job(collect_berth_status, "interval", minutes=5, id="berth_status")
    scheduler.add_job(collect_weather, "interval", minutes=5, id="weather")
    scheduler.add_job(collect_statistics, "cron", hour=2, minute=0, id="statistics_daily")
    scheduler.add_job(
        collect_berth_facilities, "cron", hour=3, minute=0, id="berth_facilities_daily"
    )
    scheduler.add_job(collect_route_gis, "cron", day_of_week="mon", hour=4, id="route_gis_weekly")
    scheduler.add_job(
        collect_tank_terminals,
        "cron",
        day_of_week="mon",
        hour=4,
        minute=30,
        id="tank_terminals_weekly",
    )

    return scheduler


async def main() -> None:
    logger.info("Starting ETL scheduler")
    scheduler = create_scheduler()
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("ETL scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main())
