from app.database import get_db
from app.core.security import get_current_user, require_role

require_admin = require_role('admin')
require_analyst = require_role('admin', 'analyst')
