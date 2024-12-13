from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os


# Helper function to validate file extensions
def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
@jwt_required()
def create_post():
    db_client = current_app.db_client
    try:
        # Get the current user's ID from JWT token
        current_user_id = get_jwt_identity()
        
        # Get post data from the request
        data = request.form
        text = data.get('text', '').strip()
        
        # Validate text content
        if not text:
            return jsonify({"error": "Post text cannot be empty"}), 400
        
        # Check text length (example: max 500 characters)
        if len(text) > 500:
            return jsonify({"error": "Post text exceeds maximum length of 500 characters"}), 400
        
        # Handle image upload
        image = request.files.get('image')
        image_path = None
        if image:
            # Validate image file
            allowed_extensions = {'png', 'jpg', 'jpeg'}
            if not allowed_file(image.filename, allowed_extensions):
                return jsonify({"error": "Invalid image file type"}), 400
            
            # Save image to a specific directory
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
        
        # Begin database transaction
        insert_basic_data_query = """
        INSERT INTO Osnovni_podaci_objave (ID, ID_Korisnika, Broj_odbijanja, Status)
        VALUES (Objave_seq.NEXTVAL, :user_id, 0, 'pending')
        """
        db_client.execute(insert_basic_data_query, {"user_id": current_user_id})

        # Sada dobijamo poslednji korišćeni ID sa CURRVAL sekvencera
        post_id_query = "SELECT Objave_seq.CURRVAL FROM dual"
        post_id = db_client.execute(post_id_query)[0][0]

        if post_id is None:
            return jsonify({"error": "Failed to retrieve post ID"}), 400

        
        # Insert into Sadrzaj_objave
        insert_content_query = """
        INSERT INTO Sadrzaj_objave (ID, Osnovni_podaci_ID, Tekst, Slika)
        VALUES (Sadrzaj_objave_seq.NEXTVAL, :post_id, :text, :image)
        """
        db_client.execute(
            insert_content_query, 
            {
                "post_id": post_id, 
                "text": text, 
                "image": image_path
            }
        )
        
        return jsonify({
            "message": "Post created successfully and is pending approval",
            "post_id": post_id
        }), 201
    
    except Exception as e:
        current_app.logger.error(f"Error creating post: {str(e)}")
        # Rollback any file upload if transaction fails
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        return jsonify({"error": "Failed to create post"}), 500




def get_user_posts(user_id):
    db_client = current_app.db_client  # Pristup bazi podataka
    
    # SQL upit za dobijanje objava korisnika
    get_posts_query = """
        SELECT 
            o.ID AS post_id, 
            o.Status AS status, 
            s.Tekst AS text, 
            s.Slika AS image
        FROM 
            Osnovni_podaci_objave o
        JOIN 
            Sadrzaj_objave s ON o.ID = s.Osnovni_podaci_ID
        WHERE 
            o.ID_Korisnika = :user_id
        ORDER BY 
            o.ID DESC
    """
    
    try:
        # Izvršavanje upita i dobijanje rezultata
        posts = db_client.execute(get_posts_query, {"user_id": user_id})
        
        # Ako nema objava
        if not posts:
            return jsonify({"message": "No posts found for this user"}), 404
        
        # Formatiranje rezultata u odgovarajući JSON
        posts_data = []
        for post in posts:
            posts_data.append({
                "post_id": post[0],  # Pristupanje post_id preko indeksa
                "status": post[1],    # Pristupanje statusu preko indeksa
                "text": post[2],      # Pristupanje tekstu preko indeksa
                "image": post[3]      # Pristupanje slici preko indeksa
            })
        
        # Vraćanje rezultata kao JSON
        return jsonify({
            "user_id": user_id,
            "posts": posts_data
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching posts for user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch posts", "details": str(e)}), 500

def update_post(post_id):
    # To do
    return jsonify({"message": f"Post {post_id} updated successfully"}), 200

def delete_post(post_id):
    # To do
    return jsonify({"message": f"Post {post_id} deleted successfully"}), 200

def get_friends_posts():
    # To do
    return jsonify({"message": "Retrieved friends' posts"}), 200
