pykirjanpito
============

Several (hacky) scripts to use with Tietokilta's accounting. As you can see,
this system is not very user-friendly at the moment.Proceed with caution.

Getting started
---------------------
1. Create virtual enviroment and install requirements.
```
pip install -r requirements.txt
```
2. Install MySQL or similar database. Create the tables from basesql.sql
3. Create file configuration.yaml and configure it with your details

```yaml
username: USERNAME # account details @ kirjanpito.tietokilta.fi
password: PASSWORD # account details @ kirjanpito.tietokilta.fi
database: mysql://username:password@localhost/kirjanpito?charset=utf8&use_unicode=0
```

4. Now you can add events to the system using
```
python add_event.py
```
5. You can check if the people have paid
```
python check_payments.py <eventid>
```
