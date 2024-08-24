const express = require('express');
const bodyParser = require('body-parser');
const bcrypt = require('bcrypt');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const cookieParser = require('cookie-parser');

const app = express();
app.use(bodyParser.urlencoded({ extended: true}));
app.use(express.static('public'));
app.use(cookieParser());

const userPassword = 'jeppe';

function authenticate(req, res, next) {
    

    console.log('loggedIn Cookie Value:', req.cookies && req.cookies.loggedIn);
    console.log('Request Cookies:', req.cookies);
    // Middleware to check authentication

    // Check if req.cookies is defined and loggedIn cookie is set to 'true'
    if (req.cookies && req.cookies.loggedIn === 'true') {
        // User is authenticated, proceed to the next middleware/route handler
        console.log('Authenticated User')
        next();
    } else {
        // User is not authenticated, send a 401 Unauthorized response
        res.status(401).send('Unauthorized: Please log in first');
    }
}

app.post('/login', async (req, res) => {

    const { password } = req.body;

    try {
        const hashedPassword = await bcrypt.hash(userPassword, 10)
        const passwordMatch = await bcrypt.compare(password, hashedPassword)

        if (passwordMatch) {
            // Password matches, set the loggedIn cookie to 'true'
            res.cookie('loggedIn', 'true' );
            res.redirect('command.html');
            console.log('Logged in successfully');

        } else {
            // Password does not match, send a 401 Unauthorized response
            res.status(401).send('Unauthorized: Invalid password');
        }
    } catch (error) {
        console.error('Error during login:', error);
        res.status(500).send('Internal Server Error');
    }
});

function exec(cmd, handler = function(error, stdout, stderr){console.log(stdout);if(error !== null){console.log(stderr)}})
    {
        const childfork = require('child_process');
        return childfork.exec(cmd, handler);
    }

app.post('/post-command', authenticate, (req, res) => {
    const { command } = req.body;
    console.log('Received command:', command);

    try {
        exec('python "C:\\Users\\Jeppe\\Codes\\In progress\\StartPersonalAssistant\\Start.py" --command "add 2 and 5" --ui')
    } catch (error) {
        console.error('Error executing command:', error);
        res.status(500).send('Internal Server Error');
    }
});

app.post('/logout', (req, res) => {
    // Clear the authentication token or session data
    
    res.clearCookie('loggedIn'); 
    
    // Redirect the user to the login page or send a response confirming logout
    res.redirect('/');
    console.log('Logged out successfully'); 
});

app.post('/command-response', (req, res) => {
    try {
        const response = req.body.text;
    
        console.log('Received response:', response);
        res.status(200).send(response);

    } catch (error) {
        console.error('Error processing response:', error);
        res.status(500).send('Internal Server Error');
    }
    
})






const PORT = process.env.PORT || 5289;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});