from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np

app = Flask(__name__)
CORS(app)

filename = 'model/laptop.pickle'
with open(filename, 'rb') as file:
    loaded_data = pickle.load(file)

model = loaded_data['best_model']
data = loaded_data['data']

def prediction(lst):
    pred_value = model.predict([lst])
    return pred_value

def company_list():
    company_columns = [col for col in data.columns if col.startswith('Company_')]
    
    if company_columns:
        company_values = data.groupby(company_columns)['Price_euros'].mean().reset_index()
        return company_values
    else:
        print("No one-hot encoded 'Company' columns found in the dataset.")
        raise ValueError("One-hot encoded 'Company' columns not found in the dataset.")
    

@app.route('/get_laptop_company', methods=['GET'])
def get_laptop_company():
    try:
        laptop_distribution = company_list()
        if 'Price_euros' in laptop_distribution.columns:
            company_list_values = [col.replace('Company_', '') for col in laptop_distribution.columns if col.startswith('Company_')]
            price_list = laptop_distribution['Price_euros'].tolist()
            return jsonify({'success': True, 'company_list': company_list_values, 'price_list': price_list})
        else:
            raise ValueError("'Price_euros' column not found in laptop_distribution.")
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    

def type_list():
    type_columns = [col for col in data.columns if col.startswith('TypeName_')]
    
    if type_columns:
        type_values = data.groupby(type_columns)['Price_euros'].mean().reset_index()
        return type_values
    else:
        print("No one-hot encoded 'Company' columns found in the dataset.")
        raise ValueError("One-hot encoded 'Company' columns not found in the dataset.")
    

@app.route('/get_laptop_types', methods=['GET'])
def get_laptop_types():
    try:
        laptop_type = type_list()
        if 'Price_euros' in laptop_type.columns:
            type_list_values = [col.replace('TypeName_', '') for col in laptop_type.columns if col.startswith('TypeName_')]
            price_list = laptop_type['Price_euros'].tolist()
            print(type_list_values,price_list)
            return jsonify({'success': True, 'type_list': type_list_values, 'price_list': price_list})
        else:
            raise ValueError("'Price_euros' column not found in laptop_type.")
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
    
    
@app.route('/get_laptop_ram', methods=['GET'])
def get_laptop_ram():
    try:
        laptop_distribution = data.groupby('Ram')['Price_euros'].mean().reset_index()
        result_json = laptop_distribution.to_json(orient='records')
        return jsonify({'success': True, 'data': result_json})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    

@app.route('/', methods=['POST', 'GET'])
def predData():
    pred_value = 0
    if request.method == 'POST':
        ram = request.form['ram']
        weight = request.form['weight']
        company = request.form['company']
        typename = request.form['typename']
        opsys = request.form['opsys']
        cpu = request.form['cpuname']
        gpu = request.form['gpuname']
        touchscreen = request.form['touchscreen']
        ips = request.form['ips']
        print(ram,weight,company,typename,opsys,cpu,gpu,touchscreen)

        feature_list = []

        feature_list.append(int(ram))
        feature_list.append(float(weight))
        feature_list.append(bool(touchscreen))
        feature_list.append(bool(ips))

        company_list = ['acer','apple','asus','dell','hp','lenovo','msi','other','toshiba']
        typename_list = ['2in1convertible','gaming','netbook','notebook','ultrabook','workstation']
        opsys_list = ['linux','mac','other','windows']
        cpu_list = ['amd','intelcorei3','intelcorei5','intelcorei7','other']
        gpu_list = ['amd','intel','nvidia']

        def traverse_list(lst, value):
            for item in lst:
                if item == value:
                    feature_list.append(1)
                else:
                    feature_list.append(0)
        
        traverse_list(company_list, company)
        traverse_list(typename_list, typename)
        traverse_list(opsys_list, opsys)
        traverse_list(cpu_list, cpu)
        traverse_list(gpu_list, gpu)

        pred_value = prediction(feature_list)
        pred_value = np.round(pred_value[0],2)*221
        print(pred_value)

        return jsonify({'pred_value': pred_value})
    
    return render_template('index.html', pred_value=pred_value)

if __name__ == '__main__':
    app.run(debug=True)