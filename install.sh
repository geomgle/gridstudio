go run *.go
cd static/xterm && npm install . && npm run webpack && cd ../..
cd terminal-server && npm install . && cd ..
cd proxy && go run manager.go
