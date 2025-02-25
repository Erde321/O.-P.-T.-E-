from app import create_app, db
from app.models import User, ActiveSession, Project, Admin, Image, ImageDetails, SelectedImage

app = create_app()

def print_table_contents():
    with app.app_context():
        # Benutzer Tabelle
        print("Benutzer Tabelle:")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Online: {user.online}, Last Active: {user.last_active}")

        # Aktive Sitzungen Tabelle
        print("\nAktive Sitzungen Tabelle:")
        sessions = ActiveSession.query.all()
        for session in sessions:
            print(f"User ID: {session.user_id}, Last Active: {session.last_active}")

        # Projekte Tabelle
        print("\nProjekte Tabelle:")
        projects = Project.query.all()
        for project in projects:
            print(f"ID: {project.id}, Name: {project.name}, Status: {project.status}, Sync: {project.sync}")

        # Admin Tabelle
        print("\nAdmin Tabelle:")
        admins = Admin.query.all()
        for admin in admins:
            print(f"ID: {admin.id}, Last Active: {admin.last_active}, Passwordhash: {admin.password}")

        # Bilder Tabelle
        print("\nBilder Tabelle:")
        images = Image.query.all()
        for image in images:
            print(f"ID: {image.id}, Project ID: {image.project_id}, Filename: {image.filename}")

        # Bilddetails Tabelle
        print("\nBilddetails Tabelle:")
        image_details = ImageDetails.query.all()
        for detail in image_details:
            print(f"Image ID: {detail.image_id}, Position: {detail.position}, Zoom: {detail.zoom}")

        # Ausgewählte Bilder Tabelle
        print("\nAusgewählte Bilder Tabelle:")
        selected_images = SelectedImage.query.all()
        for selected_image in selected_images:
            print(f"Project ID: {selected_image.project_id}, Image ID: {selected_image.image_id}")

if __name__ == '__main__':
    print_table_contents()