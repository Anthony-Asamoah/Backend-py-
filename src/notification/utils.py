from notification.schemas.notification_dispatch import NotificationStatus


async def get_status(dispatches) -> str:
    """Compute status based on dispatch statuses."""
    has_dispatches = await dispatches.aexists()
    if not has_dispatches:
        return NotificationStatus.FAILED.name

    dispatch_statuses = [d.status async for d in dispatches.all()]

    if NotificationStatus.READ.name in dispatch_statuses:
        return NotificationStatus.READ.name
    elif NotificationStatus.FAILED.name in dispatch_statuses:
        return NotificationStatus.FAILED.name
    elif NotificationStatus.PENDING.name in dispatch_statuses:
        return NotificationStatus.PENDING.name
    elif NotificationStatus.SENT.name in dispatch_statuses:
        return NotificationStatus.SENT.name
    elif NotificationStatus.DELIVERED.name in dispatch_statuses:
        return NotificationStatus.DELIVERED.name

    last_dispatch = await dispatches.alast()
    return last_dispatch.status if last_dispatch else NotificationStatus.FAILED.name


async def get_channels(dispatches) -> list[str]:
    """Get list of channels from dispatches."""
    return [channel async for channel in dispatches.values_list('channel', flat=True)]
