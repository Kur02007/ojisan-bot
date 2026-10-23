from fastapi import APIRouter

from ojisan.admin.schemas import ScheduleStatus, ScheduleUpdateRequest
from ojisan.core.config import Config
from ojisan.core.settings_store import is_live_polling_enabled, set_live_polling_enabled

router = APIRouter()


@router.get("/schedule", response_model=ScheduleStatus)
def get_schedule():
    return ScheduleStatus(
        live_polling_enabled=is_live_polling_enabled(),
        live_poll_interval_seconds=Config.LIVE_POLL_INTERVAL_SECONDS,
    )


@router.post("/schedule/live-polling", response_model=ScheduleStatus)
def update_schedule(body: ScheduleUpdateRequest):
    set_live_polling_enabled(body.live_polling_enabled)
    return ScheduleStatus(
        live_polling_enabled=body.live_polling_enabled,
        live_poll_interval_seconds=Config.LIVE_POLL_INTERVAL_SECONDS,
    )
