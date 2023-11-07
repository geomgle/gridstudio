ps -eaf | grep go | grep -v grep | awk -F" " 'system("kill -9 "$2"")'
ps -eaf | grep node | grep -v grep | awk -F" " 'system("kill -9 "$2"")'
