tell application "Terminal"
	activate
	if (count of windows) is 0 then
		do script "zsh -c $'printf \"\\033[8;60;107t\"; /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 /Users/tysonfreeze/Desktop/SavingYNAB/run.py'"
	else
		do script "zsh -c $'printf \"\\033[8;60;107t\"; /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 /Users/tysonfreeze/Desktop/SavingYNAB/run.py'" in front window
	end if
end tell
