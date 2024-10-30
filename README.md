# Start
Start is a personal assistant for your windows machine. It has plenty of good functionality
like opening games, solving math problems, taking notes and much much more. 
Start have voice functionality both for taking commands,
and answering your questions. This means that you can talk it and it will answer.

## Installation
(Make sure you have python, pip, npm and node installed)
Download the repository on to your windows machine,
and run this command to install the dependencies:
```bash
pip install --no-cache-dir -r requirements.txt
```
and
```bash
npm install express body-parser bcrypt fs path multer cookie-parser
```

## Usage

### Running with GUI
For running it open up a terminal and go to the location of the project, and run this command:
```bash
python Start.py --forceUI
```
This will now ask for a password, you just enter a pin or password that you can remember, 
this password will only be for this instance of the program. 
You are now gonna see your webbrowser open up a page here you enter your password and it is ready to use.

### Running with TUI
If you want it to just run in the terminal you just go to the location of the python file,
and run this command:
```bash
python Start.py
```

### Giving it a command directly
If you want it to just run one command and then exit, then you can run this command:
```bash
python Start.py -C "your_command_here"
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
