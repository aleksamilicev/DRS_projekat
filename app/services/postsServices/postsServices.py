from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os


@jwt_required()
def get_post_status(post_id):
    db_client = current_app.db_client
    try:
        result = db_client.execute(
            "SELECT Status FROM Osnovni_podaci_objave WHERE ID = :post_id",
            {"post_id": post_id}
        )
        if not result:
            return jsonify({"error": "Post not found"}), 404

        return jsonify({
            "post_id": post_id,
            "status": result[0][0]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting post status: {str(e)}")
        return jsonify({"error": "Failed to get post status"}), 500


@jwt_required()
def get_all_user_post_statuses():
    db_client = current_app.db_client
    user_id = get_jwt_identity()
    try:
        results = db_client.execute(
            "SELECT ID, Status FROM Osnovni_podaci_objave WHERE ID_Korisnika = :user_id ORDER BY ID DESC",
            {"user_id": user_id}
        )
        posts_status = [{"post_id": row[0], "status": row[1]} for row in results]

        return jsonify({
            "user_id": user_id,
            "posts_status": posts_status
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting all user post statuses: {str(e)}")
        return jsonify({"error": "Failed to fetch post statuses"}), 500



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
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            image.save(os.path.join(upload_folder, filename))
            image_path = f"/static/uploads/{filename}"
       
        # IZMENA: Generiši ID prvo, onda ga koristi u INSERT-u
        post_id = db_client.execute("SELECT Objave_seq.NEXTVAL FROM dual")[0][0]
        
        # Insert into Osnovni_podaci_objave using the generated ID
        insert_basic_data_query = """
        INSERT INTO Osnovni_podaci_objave (ID, ID_Korisnika, Broj_odbijanja, Status)
        VALUES (:post_id, :user_id, 0, 'pending')
        """
        db_client.execute(insert_basic_data_query, {
            "post_id": post_id,
            "user_id": current_user_id
        })
        
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
       
        # Commit the transaction
        db_client.commit()
       
        return jsonify({
            "message": "Post created successfully and is pending approval",
            "post_id": post_id
        }), 201
   
    except Exception as e:
        db_client.rollback()
        current_app.logger.error(f"Error creating post: {str(e)}")
        # Rollback any file upload if transaction fails
        if image_path and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(image_path))):
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(image_path)))
        return jsonify({"error": "Failed to create post"}), 500


@jwt_required()
def get_my_approved_posts():
    db_client = current_app.db_client
    current_user_id = get_jwt_identity()

    query = """
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
            o.ID_Korisnika = :user_id AND o.Status = 'Approved'
        ORDER BY
            o.ID DESC
    """

    try:
        posts = db_client.execute(query, {"user_id": current_user_id})

        posts_data = []
        for post in posts:
            image_url = None
            if post[3]:
                image_url = f"{request.url_root}static/uploads/{os.path.basename(post[3])}"

            posts_data.append({
                "post_id": post[0],
                "status": post[1],
                "text": post[2],
                "image": image_url,
            })

        return jsonify({
            "posts": posts_data,
            "total_posts": len(posts_data)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching approved posts for current user: {str(e)}")
        return jsonify({
            "error": "Failed to fetch your approved posts",
            "posts": []
        }), 500


@jwt_required()
def get_user_posts(username):
    db = current_app.db_client
    query = """
        SELECT
            o.ID                AS post_id,
            o.Status            AS status,
            s.Tekst             AS text,
            s.Slika             AS image,
            o.ID_Korisnika      AS user_id,
            nk.Korisnicko_ime   AS username,
            lpk.Ime             AS first_name,
            lpk.Prezime         AS last_name
        FROM  Osnovni_podaci_objave      o
        JOIN  Sadrzaj_objave             s   ON o.ID          = s.Osnovni_podaci_ID
        JOIN  Nalog_korisnika            nk  ON o.ID_Korisnika = nk.ID
        JOIN  Licni_podaci_korisnika     lpk ON o.ID_Korisnika = lpk.ID
        WHERE nk.Korisnicko_ime = :username
          AND o.Status = 'Approved'
        ORDER BY o.ID DESC
    """
    try:
        rows = db.execute(query, {"username": username})
        # Ako nema nijedne objave, provjeri da li korisnik postoji.
        if not rows:
            exists = db.execute(
                "SELECT 1 FROM Nalog_korisnika WHERE Korisnicko_ime = :u",
                {"u": username}
            )
            if not exists:
                return jsonify({"error": f"User '{username}' not found"}), 404
            return jsonify({
                "message": f"User '{username}' has no approved posts yet",
                "posts": [],
                "total_posts": 0,
                "username": username
            }), 200
        
        posts = []
        user_info = None
        for r in rows:
            # Proverava da li postoji slika i generiše URL
            image_url = None
            if r[3]:  # ako postoji slika
                image_url = f"{request.url_root}static/uploads/{os.path.basename(r[3])}"
            
            if user_info is None:
                user_info = {
                    "user_id"   : r[4],
                    "username"  : r[5],
                    "first_name": r[6],
                    "last_name" : r[7],
                }
            
            posts.append({
                "post_id" : r[0],
                "status"  : r[1],
                "text"    : r[2],
                "image"   : image_url,
                "user_id" : r[4],
                "username": r[5],
            })
        
        return jsonify({
            "posts"      : posts,
            "total_posts": len(posts),
            "user_info"  : user_info,
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching posts for user {username}: {e}")
        return jsonify({"error": "Failed to fetch user posts", "posts": []}), 500



@jwt_required()
def update_post(post_id):
    db_client = current_app.db_client  # Pristup bazi podataka
    current_user_id = get_jwt_identity()  # Pretpostavka: Funkcija za dobijanje ID ulogovanog korisnika

    # Dohvatanje podataka iz zahteva
    data = request.get_json()
    new_text = data.get("text")
    new_image = data.get("image")

    # Provera da li su svi podaci prosleđeni
    if not new_text and not new_image:
        return jsonify({"error": "No data provided for update"}), 400

    try:
        # Provera vlasništva objave
        ownership_query = """
            SELECT ID_Korisnika
            FROM Osnovni_podaci_objave
            WHERE ID = :post_id
        """
        result = db_client.execute(ownership_query, {"post_id": post_id})

        # Proveri da li je lista prazna
        if not result:
            return jsonify({"error": "Post not found"}), 404
        
        owner = result[0]

        user_id = owner[0]
        # Konverzija current_user_id u integer
        current_user_id = int(current_user_id)

        if user_id != current_user_id:
            return jsonify({"error": "You are not authorized to edit this post"}), 403

        # Ažuriranje teksta ako postoji nova vrednost
        if new_text:
            update_text_query = """
            UPDATE Sadrzaj_objave
            SET Tekst = :text
            WHERE Osnovni_podaci_ID = :post_id
            """
            db_client.execute(update_text_query, {"text": new_text, "post_id": post_id})

        # Ažuriranje slike ako postoji nova vrednost
        if new_image:
            update_image_query = """
            UPDATE Sadrzaj_objave
            SET Slika = :image
            WHERE Osnovni_podaci_ID = :post_id
            """
            db_client.execute(update_image_query, {"image": new_image, "post_id": post_id}) 

        return jsonify({"message": "Post updated successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error updating post {post_id}: {str(e)}")
        return jsonify({"error": "Failed to update post", "details": str(e)}), 500




@jwt_required()
def delete_post(post_id):
    db_client = current_app.db_client
    current_user_id = get_jwt_identity()  # ID trenutnog korisnika

    try:
        # Provera vlasništva objave
        ownership_query = """
        SELECT ID_Korisnika
        FROM Osnovni_podaci_objave
        WHERE ID = :post_id
        """
        result = db_client.execute(ownership_query, {"post_id": post_id})

        if not result:
            return jsonify({"error": f"Post with ID {post_id} does not exist"}), 404

        owner = result[0]

        user_id = owner[0]
        # Konverzija current_user_id u integer
        current_user_id = int(current_user_id)

        if user_id != current_user_id:
            return jsonify({"error": "You are not authorized to delete this post"}), 403

        # Brisanje iz `Sadrzaj_objave`
        delete_content_query = """
        DELETE FROM Sadrzaj_objave
        WHERE Osnovni_podaci_ID = :post_id
        """
        db_client.execute(delete_content_query, {"post_id": post_id})

        # Brisanje iz `Osnovni_podaci_objave`
        delete_post_query = """
        DELETE FROM Osnovni_podaci_objave
        WHERE ID = :post_id
        """
        db_client.execute(delete_post_query, {"post_id": post_id})

        return jsonify({"message": f"Post {post_id} deleted successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting post {post_id}: {str(e)}")
        return jsonify({"error": "An error occurred while deleting the post", "details": str(e)}), 500





#potencijalna greska, treba testirati, imamo 2 prijatelja(1. ima pending objave, 2. ima approved), da li ce
# nam vratiti listu approved objava ili cim naidje na pending da ce odma reci da nema approved objava
# Dodao sam flag da kontrolise ovo, ali ukoliko bude bio neki bug, treba se vratiti ovde
@jwt_required()
def get_friends_posts():
    db_client = current_app.db_client  # Access to the database from the Flask application
    
    try:
        # Get the authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()  # Assuming you have this function implemented
        
        if not current_user_id:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Query to fetch friends of the current user
        friends_query = """
        SELECT 
            lpk.ID AS friend_id
        FROM 
            Prijateljstva p
        JOIN 
            Licni_podaci_korisnika lpk 
            ON (CASE 
                    WHEN p.ID_Korisnika1 = :user_id THEN p.ID_Korisnika2
                    ELSE p.ID_Korisnika1
                END) = lpk.ID
        WHERE 
            (p.ID_Korisnika1 = :user_id OR p.ID_Korisnika2 = :user_id) 
            AND p.Status = 'Accepted'
        """
        
        # Execute the query to get friends' IDs
        friends = db_client.execute_query(friends_query, {"user_id": current_user_id})
        
        # If there are no friends, return a message
        if not friends:
            return jsonify({"message": "You have no friends"}), 200
        
        friends_ids = [friend.friend_id for friend in friends]
        
        # Prepare a list to store the posts from friends
        all_posts = []
        
        # Flag to track if we have any approved posts
        has_approved_posts = False
        
        # For each friend, get their posts using the existing get_user_posts method
        for friend_id in friends_ids:
            # Get posts from friend
            posts = get_user_posts(friend_id)
            
            # Filter posts by 'approved' status and collect them
            for post in posts:
                if post["status"] == "approved":
                    all_posts.append(post)
                    has_approved_posts = True
        
        # If no approved posts were found, return a message
        if not has_approved_posts:
            return jsonify({"message": "Your friends have no approved posts"}), 200
        
        # Return all the posts from friends
        return jsonify({
            "message": "Friends' posts retrieved successfully",
            "posts": all_posts,
            "total_posts": len(all_posts)
        }), 200
    
    except Exception as e:
        # Error handling
        current_app.logger.error(f"Error retrieving friends' posts: {e}")
        return jsonify({"error": "Internal server error"}), 500



