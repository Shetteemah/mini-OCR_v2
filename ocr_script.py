import easyocr
import numpy as np
import cv2
from PIL import Image
import os
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
                angle = -1.55
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

header_height = img_height * 0.185  # Assuming header occupies 10% of the image height
footer_height = img_height * 0.9  # Assuming footer occupies 10% of the image height
main_content_top = header_height
main_content_bottom = footer_height
main_content_height = main_content_bottom - main_content_top

# column_width = img_width / 3
left_column_width = img_width * 0.48
middle_column_start = left_column_width
middle_column_width = img_width * 0.19
right_column_start = middle_column_start + middle_column_width
footnote_keywords = [
    "FB Befundvorlage Motoriklabor Parkinson prae op",
    "Seite 4 von 5",
    "Ausgedruckt unterliegt das Dokument nicht dem Änderungsdienst"
]

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
    is_footnote = y_coord > footer_height * 0.9 or any(keyword in text for keyword in footnote_keywords)
    if 'ID:' in text:
        doc_id = text.split('ID:')[1].strip()
    if 'Rev.-Index:' in text:
        rev_index = text.split('Rev.-Index: ')[1].strip()

    if not is_footnote and main_content_top <= y_coord <= main_content_bottom:
        if x_coord < left_column_width:
            left_column.append(text)
        elif x_coord < right_column_start:
            middle_column.append(text)
        else:
            right_column.append(text)

    # if not is_footnote:
    #     if x_coord < column_width:
    #         left_column.append(text)
    #     elif x_coord < 2 * column_width:
    #         middle_column.append(text)
    #     else:
    #         right_column.append(text)        

img_cv = cv2.imread(preprocessed_image_path)
header_img = img_cv[0:int(header_height), 0:img_width]
cv2.imwrite('temp/header.png', header_img)
footer_img = img_cv[int(footer_height):img_height, 0:img_width]
cv2.imwrite('temp/footer.png', footer_img)
main_content_img = img_cv[int(main_content_top):int(main_content_bottom), 0:img_width]
cv2.imwrite('temp/main_content.png', main_content_img)

left_column_img = main_content_img[0:int(main_content_height), 0:int(left_column_width)]
cv2.imwrite('temp/left_column.png', left_column_img)
middle_column_img = main_content_img[0:int(main_content_height), int(middle_column_start):int(right_column_start)]
cv2.imwrite('temp/middle_column.png', middle_column_img)
right_column_img = main_content_img[0:int(main_content_height), int(right_column_start):img_width]
cv2.imwrite('temp/right_column.png', right_column_img)

header_text = pytesseract.image_to_string(header_img, lang='deu', config='--oem 3 --psm 3')
# left_column_text = pytesseract.image_to_string(left_column_img, lang='deu')
middle_column_text = pytesseract.image_to_string(middle_column_img, lang='deu', config='--oem 3 --psm 3')
right_column_text = pytesseract.image_to_string(right_column_img, lang='deu', config='--oem 3 --psm 3')

header = header_text.split('\n')
# left_column = left_column_text.split('\n')
# middle_column = middle_column_text.split('\n')
# right_column = right_column_text.split('\n')
middle_column = [line.strip() for line in middle_column_text.split('\n') if line.strip()]
right_column = [line.strip() for line in right_column_text.split('\n') if line.strip()]
header = [line.strip() for line in header if line.strip()]

print("\n\nHeader Text:")
for text in header:
    print(text)
print("\n\nLeft Column Text:")
for text in left_column:
    print(text)
print("\n\nMiddle Column Text:")
for text in middle_column:
    print(text)
print("\n\nRight Column Text:")
for text in right_column:
    print(text)
print(f"\n\nDocument ID: {doc_id}")
print(f"Revision Index: {rev_index}")
