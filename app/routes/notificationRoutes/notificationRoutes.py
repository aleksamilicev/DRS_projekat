from flask import Blueprint
from ...services.notificationServices.notificationServices import (
    create_notification,
    get_notifications,
    get_notification_by_id,
    update_notification,
    mark_notification_as_read,
    delete_notification
)

api = Blueprint('api', __name__)

# Notifications routes
api.add_url_rule('/notifications', view_func=create_notification, methods=['POST']) 
api.add_url_rule('/notifications', view_func=get_notifications, methods=['GET'])  
api.add_url_rule('/notifications/<int:notification_id>', view_func=get_notification_by_id, methods=['GET'])  
api.add_url_rule('/notifications/<int:notification_id>', view_func=update_notification, methods=['PUT'])  
api.add_url_rule('/notifications/<int:notification_id>/read', view_func=mark_notification_as_read, methods=['PUT']) 
api.add_url_rule('/notifications/<int:notification_id>', view_func=delete_notification, methods=['DELETE'])  
