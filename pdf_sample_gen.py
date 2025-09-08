from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def create_fra_pdf(filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 50
    line_height = 20

    lines = [
        "FORM – A",
        "CLAIM FORM FOR RIGHTS TO FOREST LAND",
        "[See Rule 11(1)(a)]",
        "",
        "1. Name of the claimant(s): Ram Singh",
        "2. Name of the spouse: Sita Devi",
        "3. Name of father/mother: Mohan Singh",
        "4. Address: Village Road, Bhilgaon",
        "5. Village: Bhilgaon",
        "6. Gram Panchayat: Bhilgaon GP",
        "7. Tehsil/Taluka: Dharni",
        "8. District: Amravati",
        "9. State: Maharashtra",
        "",
        "9(a). Scheduled Tribe: Yes",
        "9(b). Other Traditional Forest Dweller: No",
        "Tribe name: Gond",
        "",
        "10. Area of land claimed: 3.5 hectares",
        "Survey No: 45/2",
        "",
        "Claim status: Approved",
        "Patta No: PATTA/2025/091",
        "Date of DLC decision: 25/08/2025"
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= line_height

    c.showPage()
    c.save()


if __name__ == "__main__":
    create_fra_pdf("sample_docs/sample_fra.pdf")
    print("✅ sample_fra.pdf created successfully!")