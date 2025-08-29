import easyocr
import numpy as np
import cv2
from PIL import Image
import os
import shutil
import pytesseract

def image_preprocessing(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # img = cv2.equalizeHist(img)
    # _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    def deskew_image(image):
        _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[-1] # Get the rotation angle in degrees
            print(f'Initial skew angle: {angle:.2f} degrees')
            if angle < -45:
                angle = 90 + angle
            elif angle > 45:
                angle = -1
            elif angle > 0 and angle < 45:
                angle = -angle
            elif angle < 0 and angle > -45:
                angle = 90 + angle
            if angle < 0:
                angle = -angle
            # else:
            #     angle = -angle
            (h, w) = image.shape
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated, angle
        return image, 0
    img, skew_angle = deskew_image(img)
    print(f'Deskew angle applied: {skew_angle:.2f} degrees')
    # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    # img = cv2.fastNlMeansDenoising(img)
    if 'temp' not in os.listdir('.'):
        os.makedirs('temp')
    preprocessed_image_path = 'temp/preprocessed_image.png'
    cv2.imwrite(preprocessed_image_path, img)
    return preprocessed_image_path

reader = easyocr.Reader(['de'], gpu=False)
image_path = 'images/MDS-UPDRS_page-0001.png'
preprocessed_image_path = image_preprocessing(image_path)
results = reader.readtext(preprocessed_image_path)

# print("\nEasyOCR Output:")
# for (bbox, text, prob) in results:
#     print(text)

# text = pytesseract.image_to_string(image_path, lang='deu')
# print("\n\nTesseract OCR Output:")
# print(text)

img = Image.open(preprocessed_image_path)
img_width, _ = img.size
img_height = img.size[1]

header_height = int(img_height * 0.185)
footer_height = int(img_height * 0.94)
main_content_top = header_height
main_content_bottom = footer_height
main_content_height = main_content_bottom - main_content_top
left_column_start = 0
left_column_width = int(img_width * 0.48)
middle_column_start = left_column_width
middle_column_width = int(img_width * 0.19)
right_column_start = middle_column_start + middle_column_width

main_content_top_mds_updrs_p2 = header_height
main_content_bottom_mds_updrs_p2 = footer_height
main_content_height_mds_updrs_p2 = main_content_bottom_mds_updrs_p2 - main_content_top_mds_updrs_p2
left_column_start_mds_updrs_p2 = 0
left_column_width_mds_updrs_p2 = int(img_width * 0.48)
middle_column_start_mds_updrs_p2 = left_column_width_mds_updrs_p2
middle_column_width_mds_updrs_p2 = int(img_width * 0.19)
right_column_start_mds_updrs_p2 = middle_column_start_mds_updrs_p2 + middle_column_width_mds_updrs_p2

header_height_updrs = int(img_height * 0.235)
footer_height_updrs = int(img_height * 0.9)
main_content_top_updrs = int(header_height_updrs)
main_content_bottom_updrs = footer_height_updrs
main_content_height_updrs = main_content_bottom_updrs - main_content_top_updrs
left_column_start_updrs = 0
left_column_width_updrs = img_width * 0.49
middle_column_start_updrs = left_column_width_updrs
middle_column_width_updrs = img_width * 0.19
right_column_start_updrs = middle_column_start_updrs + middle_column_width_updrs

footnote_keywords = [
    "FB Befundvorlage Motoriklabor Parkinson prae op",
    "Seite 4 von 5",
    "Ausgedruckt unterliegt das Dokument nicht dem Änderungsdienst"
]

header_text = []
footer_text = []
main_content_text = []

left_column = []
middle_column = []
right_column = []
header = []

doc_id = None
rev_index = None


for detection in results:
    # print('\n\n', text)
    bbox, text, _ = detection
    x_coord = bbox[0][0]
    y_coord = bbox[0][1]
    
    if y_coord < main_content_top:
        header_text.append(text)
    elif y_coord > main_content_bottom:
        footer_text.append(text)
    else:
        main_content_text.append(text)

    if 'ID:' in text:
        doc_id = text.split('ID:')[1].strip()
    if 'Rev.-Index:' in text:
        rev_index = text.split('Rev.-Index: ')[1].strip()

header_text = set(header_text)
footer_text = set(footer_text)
main_content_text = set(main_content_text)

mds_updrs_page1_sections = {"Teil I A Komplexes Verhalten", "Teil I B Komplexes Verhalten", "Teil II Motorische Aspekte bei Erfahrungen"}
mds_updrs_page2_sections = {"Teil III Untersuchung der Motorik", "Teil IV Motorische Komplikationen"}
updrs_page1_sections = {"I. Kognitive Funktionen, Verhalten und Stimmung", "II. Aktivitäten des tägl. Lebens", "III. Untersuchung der Motorik"}
updrs_page2_sections = {"IV. Komplikationen der Behandlung", "V. Modifizierte Stadieneinteilung nach Hoehn u. Yahr", "VI. Modifizierte Bewertungsskala der Aktiviäten des tägl. Lebens nach Schwab u. England"}

if 'MDS- UPDRS' not in header_text and 'U.PD.RS' not in header_text:
    header_text = []
print("\n\nHeader Text Set:", header_text)
# print("\n\nHeader Text[1]:", list(header_text)[4])
print("\n\nFooter Text Set:", footer_text)
print("\n\nMain Content Text Set:", main_content_text)

is_mds_updrs_page1 = (
    # print("Debugging is_mds_updrs_page1: ", 'MDS- UPDRS' in header_text,
        #   any(keyword in footer_text for keyword in footnote_keywords[:3]),
        #   all(section in main_content_text for section in mds_updrs_page1_sections)),
   'MDS- UPDRS' in header_text and
   any(keyword in footer_text for keyword in footnote_keywords[:3])
)
is_mds_updrs_page2 = (
    # print("Debugging is_mds_updrs_page2: ", len(header_text) == 0,
    #       any(keyword in footer_text for keyword in footnote_keywords[:3]),
    #       all(section in main_content_text for section in mds_updrs_page2_sections)),
    len(header_text) == 0 and
    any(keyword in footer_text for keyword in footnote_keywords[:3])
)
is_updrs_page1 = (
    # print("Debugging is_updrs_page1: ", 'U.PD.RS' in header_text,
        #   len(footer_text) == 0,
        #   all(section in main_content_text for section in updrs_page1_sections)),
    'U.PD.RS' in header_text and
    len(footer_text) == 0
)
is_updrs_page2 = (
    # print("Debugging is_updrs_page2: ", len(header_text) == 0,
    #       len(footer_text) == 0,
    #       all(section in main_content_text for section in updrs_page2_sections)),
    len(header_text) == 0 and
    len(footer_text) == 0
)

img_cv = cv2.imread(preprocessed_image_path)

if is_mds_updrs_page1:
    print("\n\nDetected: Page 1 of MDS-UPDRS form")
    header_img = img_cv[0:int(header_height), 0:img_width]
    main_content_img = img_cv[main_content_top:main_content_bottom, 0:img_width]
    footer_img = img_cv[main_content_bottom:img_height, 0:img_width]
    left_column_img = main_content_img[:, 0:int(left_column_width)]
    middle_column_img = main_content_img[:, int(left_column_width):int(right_column_start)]
    right_column_img = main_content_img[:, int(right_column_start):img_width]
elif is_mds_updrs_page2:
    print("\n\nDetected: Page 2 of MDS-UPDRS form")
    main_content_img = img_cv[0:main_content_bottom_mds_updrs_p2, 0:img_width]
    footer_img = img_cv[main_content_bottom_mds_updrs_p2:img_height, 0:img_width]
    left_column_img = main_content_img[:, 0:int(left_column_width_mds_updrs_p2)]
    middle_column_img = main_content_img[:, int(left_column_width_mds_updrs_p2):int(right_column_start_mds_updrs_p2)]
    right_column_img = main_content_img[:, int(right_column_start_mds_updrs_p2):img_width]
elif is_updrs_page1:
    print("\n\nDetected: Page 1 of UPDRS form")
    header_img = img_cv[0:main_content_top_updrs, 0:img_width]
    main_content_img = img_cv[main_content_top_updrs:img_height, 0:img_width]
    left_column_img = main_content_img[:, 0:int(left_column_width_updrs)]
    middle_column_img = main_content_img[:, int(left_column_width_updrs):int(right_column_start_updrs)]
    right_column_img = main_content_img[:, int(right_column_start_updrs):img_width]
elif is_updrs_page2:
    print("\n\nDetected: Page 2 of UPDRS form")
    section_iv_end = int(img_height * 0.465)
    section_v_end = int(img_height * 0.598)
    main_content_img = img_cv[0:img_height, 0:img_width]
    iv_section_img = img_cv[0:section_iv_end, 0:img_width]
    v_section_img = img_cv[section_iv_end:section_v_end, 0:img_width]
    vi_section_img = img_cv[section_v_end:img_height, 0:img_width]
else:
    print("\n\nForm type could not be determined. Proceeding with default segmentation.")
    header_img = img_cv[0:main_content_top, 0:img_width]
    main_content_img = img_cv[main_content_top:main_content_bottom, 0:img_width]
    footer_img = img_cv[main_content_bottom:img_height, 0:img_width]
    left_column_img = main_content_img[:, 0:int(left_column_width)]
    middle_column_img = main_content_img[:, int(left_column_start):int(right_column_start)]
    right_column_img = main_content_img[:, int(right_column_start):img_width]

# if os.path.exists('temp'):
#     shutil.rmtree('temp')
# os.makedirs('temp')

if is_mds_updrs_page1 or is_updrs_page1:
    cv2.imwrite('temp/header.png', header_img)
if is_mds_updrs_page1 or is_mds_updrs_page2:
    cv2.imwrite('temp/footer.png', footer_img)
if is_updrs_page2:
    cv2.imwrite('temp/main_content.png', main_content_img)
    cv2.imwrite('temp/section_IV.png', iv_section_img)
    cv2.imwrite('temp/section_V.png', v_section_img)
    cv2.imwrite('temp/section_VI.png', vi_section_img)
else:
    cv2.imwrite('temp/main_content.png', main_content_img)
    cv2.imwrite('temp/left_column.png', left_column_img)
    cv2.imwrite('temp/middle_column.png', middle_column_img)
    cv2.imwrite('temp/right_column.png', right_column_img)

if is_mds_updrs_page1 or is_updrs_page1:
    header_text = pytesseract.image_to_string(header_img, lang='deu', config='--oem 3 --psm 3')
    header = header_text.split('\n')
if not is_updrs_page2:
    left_column_text = pytesseract.image_to_string(left_column_img, lang='deu')
    middle_column_text = pytesseract.image_to_string(middle_column_img, lang='deu', config='--oem 3 --psm 3')
    right_column_text = pytesseract.image_to_string(right_column_img, lang='deu', config='--oem 3 --psm 3')
    middle_column = middle_column_text.split('\n')
    right_column = right_column_text.split('\n')
    left_column = [line.strip() for line in left_column_text.split('\n') if line.strip()]
else:
    iv_section_text = pytesseract.image_to_string(iv_section_img, lang='deu', config='--oem 3 --psm 3')
    v_section_text = pytesseract.image_to_string(v_section_img, lang='deu', config='--oem 3 --psm 3')
    vi_section_text = pytesseract.image_to_string(vi_section_img, lang='deu', config='--oem 3 --psm 3')
    left_column = [line.strip() for line in iv_section_text.split('\n') if line.strip()]
    middle_column = [line.strip() for line in v_section_text.split('\n') if line.strip()]
    right_column = vi_section_text.split('\n')


if is_mds_updrs_page1 or is_updrs_page1:
    print("\n\nHeader Text:\n")
    for text in header:
        print(text)
print("\n\nLeft Column Text:\n")
for text in left_column:
    print(text)
print("\n\nMiddle Column Text:\n")
for text in middle_column:
    print(text)
print("\n\nRight Column Text:\n")
for text in right_column:
    print(text)
print(f"\n\nDocument ID: {doc_id}")
print(f"Revision Index: {rev_index}")
