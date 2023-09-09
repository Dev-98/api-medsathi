# ALL THE LIBRARY THIS PROJECT USES
from flask import Flask , request, jsonify
import easyocr, os
from PIL import Image
import pandas as pd
from thefuzz import fuzz
from string import digits, punctuation

# DEFINING OBJECT
app = Flask(__name__)

# DEFINIG FIRST PAGE 
@app.route('/')
def main():
	return ' HELLO WORLD '

@app.route('/predict', methods=['POST'])
def predict():

	image = request.files['image']

	path = Image.open(image.stream)
	reader = easyocr.Reader(['en'])

	results = reader.readtext(path)
	
	text = ' ' 
	for result in results:
		text += result[1] + ' '

	# print(p,'\n',text,'\n',p)

	remove_digits = str.maketrans('', '', punctuation)
	remove_digits2 = str.maketrans('', '', digits)

	res = text.translate(remove_digits)
	res = res.translate(remove_digits2)

	new_text = ""
	for word in str(res).split():
		if (len(word) > 4):
			new_text += word + " "

	# print(p,'\n',new_text,'\n',p)
	data = pd.read_csv("medicine_data.csv")
	
	l=[]

	for i in data["Medicine"]:
		score = fuzz.partial_token_sort_ratio(i, new_text)
		l.append(score)
		index = sorted(list(enumerate(l)), reverse=True, key=lambda x: x[1])[0][0]
		if max(l) >= 80:
			bimari = data["Disease"][index]
			dawai = data["Medicine"][index]
			out = {'Ailments': bimari, 'Medicine': dawai}
		else :
			bimari = 'Not available in database'
			dawai = 'Unreadable image'
			out = {'Ailments': bimari, 'Medicine': dawai}

			
	return jsonify(out)


if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080))) 
