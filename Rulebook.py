# Create a PDF using reportlab with the provided rulebook

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("Fantasy_Cricket_Rulebook.pdf")
styles = getSampleStyleSheet()

elements = []

def add_title(text):
    elements.append(Paragraph(f"<b>{text}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

def add_heading(text):
    elements.append(Paragraph(f"<b>{text}</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))

def add_text(text):
    elements.append(Paragraph(text, styles["Normal"]))
    elements.append(Spacer(1, 6))

def add_table(data):
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

# Title
add_title("Fantasy Cricket Points Rulebook")

# Batting
add_heading("1. Batting Points")
add_text("Runs: +1 point each<br/>Fours: +2 points each<br/>Sixes: +3 points each")

add_heading("Strike Rate Bonus/Penalty")
add_table([
    ["Strike Rate", "Points"],
    ["< 50", "-25"],
    ["50 – 69", "-20"],
    ["70 – 89", "-15"],
    ["90 – 109", "0"],
    ["110 – 129", "+15"],
    ["130 – 149", "+20"],
    ["150 – 174", "+30"],
    ["≥ 175", "+40"],
])

add_heading("Batting Milestones")
add_text("50+ runs: +25<br/>75+ runs: +35<br/>100+ runs: +50")

add_heading("Duck Penalty")
add_text("Dismissed for 0 runs (non-bowlers): -10")

# Bowling
add_heading("2. Bowling Points")
add_text("Wicket: +30<br/>Dot Ball: +2<br/>Maiden Over: +25")

add_heading("Economy Rate Bonus/Penalty")
add_table([
    ["Economy", "Points"],
    ["< 3", "+50"],
    ["3 – 3.99", "+40"],
    ["4 – 4.99", "+35"],
    ["5 – 5.99", "+25"],
    ["6 – 8.99", "+20"],
    ["9 – 10.99", "+5"],
    ["11 – 12.99", "-10"],
    ["≥ 13", "-20"],
])

add_heading("Bowling Milestones")
add_text("2 wickets: +25<br/>3–4 wickets: +40<br/>5+ wickets: +70")

add_heading("Bonus Wickets")
add_text("Bowled: +10<br/>LBW: +10")

# Fielding
add_heading("3. Fielding Points")
add_text("Catch: +10<br/>Stumping: +10<br/>Direct Runout: +10<br/>Assist Runout: +5")

# Bonus
add_heading("4. Special Bonus")
add_text("Man of the Match: +30")

# Multipliers
add_heading("5. Multipliers")
add_text("Captain: 2×<br/>Vice Captain: 1.5×<br/>Trump Card (after Match 35): 3×<br/>Triple Captain: 3×")

# Build PDF
doc.build(elements)