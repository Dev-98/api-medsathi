# ALL THE LIBRARY THIS PROJECT USES
from flask import Flask , request, jsonify
from flask_cors import CORS
import easyocr, os
from PIL import Image
import pandas as pd
from thefuzz import fuzz
from string import digits, punctuation

# DEFINING OBJECT
app = Flask(__name__)
CORS(app)

# DEFINIG FIRST PAGE 
@app.route('/')
def main():
	return ' HELLO WORLD '


@app.route('/predict', methods=['GET','POST'])
def predict():

	if request.method == 'POST':
		image = request.files['image']

		try:
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

			print("Name = ",new_text.lower())

			for i in data["Medicine_Name"]:
				score = fuzz.partial_token_sort_ratio(i.lower(), new_text.lower())
				l.append(score)
				index = sorted(list(enumerate(l)), reverse=True, key=lambda x: x[1])[0][0]
				# print("\n Score = ",max(l))
				if max(l) >= 80:
					uses = data["Uses"][index]
					dawai = data["Medicine_Name"][index]
					effects = data["Side_effects"][index]
					url = data["Image URL"][index]

					out = {'Use cases': uses, 'Medicine': dawai, 'effects': effects, 'image_url': url}

				else :
					
					not_found = 'Not available in database, Unreadable image'

					out = {'Not Found': not_found}

			return jsonify(out), 200

		except Exception as e :

			return jsonify({'error': e}), 500

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080))) 
