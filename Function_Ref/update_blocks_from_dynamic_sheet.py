import win32com.client
from openpyxl import load_workbook

# ===== EXCEL FILE =====
excel_file = r"C:\Users\Nextkraft\Documents\cad command by excel\level_data.xlsm"
sheet_name = "DYNAMIC BLOCK PARMATER"

wb = load_workbook(excel_file, data_only=True)
sheet = wb[sheet_name]

# ===== SAFE VALUE FUNCTION =====
def get_val(cell):
    val = sheet[cell].value
    if val is None or val == "":
        return None
    try:
        return float(val)
    except:
        return None

# ===== BLOCK CONFIG (FINAL) =====
block_data = {
    "PALLET_DYN_BLOCK": {
        "X": get_val("C5"),
        "Y": get_val("D5")
    },
    "COUNTER_WEIGHT_DYN_BLOCK": {
        "X": get_val("C6"),
        "Y": None
    },
    "TRANSPORTER_DYN_BLOCK": {
        "X": None,
        "Y": get_val("D7")
    },
    "RCC_BRACKET_DYN_BLOCK": {
        "X": get_val("C8"),
        "Y": None
    },
    "RCC_DYN_BLOCK": {
        "X": get_val("C9"),
        "Y": get_val("D9")
    }
}

print("\n📊 Excel Values Loaded:")
for blk, vals in block_data.items():
    print(f"{blk} → X={vals['X']} | Y={vals['Y']}")

# ===== CONNECT AUTOCAD =====
try:
    acad = win32com.client.GetActiveObject("AutoCAD.Application")
    print("\n✅ Connected to running AutoCAD")
except:
    acad = win32com.client.Dispatch("AutoCAD.Application")
    print("\n🚀 Started new AutoCAD")

doc = acad.ActiveDocument
ms = doc.ModelSpace

print("\n🔍 Scanning drawing for matching blocks...\n")

updated = 0
skipped = 0

# ===== LOOP THROUGH ENTITIES =====
for entity in ms:
    if entity.ObjectName == "AcDbBlockReference":

        name = entity.EffectiveName

        if name in block_data:
            print(f"🎯 Found Block: {name}")

            try:
                props = entity.GetDynamicBlockProperties()
            except:
                print("   ⚠️ No dynamic properties found")
                continue

            for prop in props:
                pname = prop.PropertyName.upper()
                val = block_data[name]

                # ===== APPLY X =====
                if val["X"] is not None and pname in ["X", "DISTANCE1", "WIDTH"]:
                    try:
                        prop.Value = val["X"]
                        print(f"   ➤ X Updated → {val['X']}")
                        updated += 1
                    except:
                        print("   ❌ Failed to update X")

                # ===== APPLY Y =====
                if val["Y"] is not None and pname in ["Y", "DISTANCE2", "LENGTH"]:
                    try:
                        prop.Value = val["Y"]
                        print(f"   ➤ Y Updated → {val['Y']}")
                        updated += 1
                    except:
                        print("   ❌ Failed to update Y")

        else:
            skipped += 1

print(f"\n✅ Total Parameters Updated: {updated}")
print(f"⏭️ Blocks Skipped: {skipped}")

# ===== REGEN + SAVE =====
try:
    doc.Regen(1)
    doc.Save()
    print("💾 Drawing Saved Successfully")
except:
    print("⚠️ Please save drawing manually (CTRL+S)")

print("\n🚀 ALL DYNAMIC BLOCKS UPDATED SUCCESSFULLY")