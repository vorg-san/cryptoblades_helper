This was a personal private project that I coded to help me play CryptoBlades optimally. 

This project includes:
  - listing of all the money BNB (binance cryptocurrency) and SKILL (cryptoblades cryptocurrency) in your addresses and their worth in dollar value reading directly from pancakeswap smart contract pools
  - listing all the cryptoblades characters and weapons you hold as NFTs in each address
  - interacting with cryptoblades smartcontracts to see if the time to fight has come and execute fights (signs transaction with your private key) and, also, to read data from the market place and buy chars and weapons if they are cheap


Backend:

install and run mysql
create .env file:
 DJANGO_RECIPE_MANAGER_SECRET_KEY=''
 MYSQL_USER=''
 MYSQL_PASS=''
 MYSQL_HOST=''
 pks=''
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver

Frontend:

cd frontend
npm i
export NODE_OPTIONS=--openssl-legacy-provide
npm start