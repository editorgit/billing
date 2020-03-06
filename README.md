# Very simple Billing: Test task


### Tests
```bash
./manage.py test transfer.tests
```

### How it work:
#### docker-compose up
###### Available currencies: 'EUR', 'USD', 'GBP', 'RUB'
###### Defualt currency: 'EUR'

#### Create user
```bash
http://localhost:1234/signup/ POST {"username": "email", "password": "pass",
                                    "currency": "USD", "amount": 323}
``` 

#### Login user
```bash
http://localhost:1234/login/ POST {"username": "email", "password": "pass"}
``` 

#### Make transfer
```bash
http://localhost:1234/transfer/ POST {"sender": "email", "receiver": "email",
                                      "amount": 323}
``` 