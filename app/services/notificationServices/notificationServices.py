from flask import jsonify, request

from flask import jsonify, request

# Notifications route functions
def create_notification():
    print('keke')
    return jsonify({"message": "Notification created successfully"}), 201

def get_notifications():
    # To do
    return jsonify({"message": "Retrieved notifications"}), 200

def get_notification_by_id(notification_id):
    # To do
    return jsonify({"message": f"Retrieved notification {notification_id}"}), 200

def update_notification(notification_id):
    # To do
    return jsonify({"message": f"Notification {notification_id} updated successfully"}), 200

def mark_notification_as_read(notification_id):
    # To do
    return jsonify({"message": f"Notification {notification_id} marked as read"}), 200

def delete_notification(notification_id):
    # To do
    return jsonify({"message": f"Notification {notification_id} deleted successfully"}), 200
