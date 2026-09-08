# Cycle Navigator separation

Live/native Handlekompas context is contextual only for Cycle Navigator. It must never silently rewrite a frozen weekly Cycle Navigator signal, forecast range, score, rotation ladder, altseason countdown, or public issue state. DEGRADED/unavailable context remains explicit; null forecast ranges remain unpublished.
