from utils.upload_to_imgur import upload_to_imgur


test_image_path = "/Users/kshitijbanka/finance-newletter/attachments/Infosys/0.png"

# Upload and print the public URL
public_url = upload_to_imgur(test_image_path, "{clientId}")
print(f"Uploaded image URL: {public_url}")