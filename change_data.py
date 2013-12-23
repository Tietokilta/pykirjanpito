import tik
from configuration import configuration
tikapi = tik.TIK(configuration['username'], configuration['password'])
for raw_id in range(12087, 12104):
    form_data = tikapi.get_form_values(raw_id)
    if len(form_data['entry[date(1i)]']) == 2:
        form_data['entry[date(1i)]'] = '20'+form_data['entry[date(1i)]']
    form_data['entry[receipt_number]'] = str(int(form_data['entry[receipt_number]'])-451)
    tikapi.set_form_values(raw_id, form_data)
    print "RAW_ID: %s processed" % raw_id
print form_data