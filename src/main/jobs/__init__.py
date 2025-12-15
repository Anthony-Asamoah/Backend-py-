from auth.jobs.prune_expired_revoked_tokens import cleanup_expired_revoked_tokens
from main.jobs.cleanup_inmemory_cache import cleanup_inmemory_cache
from main.utils.dependency_injection import MethodsContainer

scheduled_jobs = MethodsContainer()

# main jobs
scheduled_jobs.register(cleanup_inmemory_cache, "cron", minute='*/5')

# auth jobs
scheduled_jobs.register(cleanup_expired_revoked_tokens, "cron", minute=0, hour=0)
