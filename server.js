const express = require("express");
const bodyParser = require("body-parser");
const bcrypt = require("bcrypt");
const fs = require("fs");
const path = require("path");
const multer = require("multer");
const cookieParser = require("cookie-parser");

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static("public"));
app.use(cookieParser());
app.use(bodyParser.json());

var userPassword = "0000";
var response = "";
var newResponse = false;
var questionAsked = false;
var questionType = "";

function authenticate(req, res, next) {
  console.log("loggedIn Cookie Value:", req.cookies && req.cookies.loggedIn);
  console.log("Request Cookies:", req.cookies);
  // Middleware to check authentication

  // Check if req.cookies is defined and loggedIn cookie is set to 'true'
  if (req.cookies && req.cookies.loggedIn === "true") {
    // User is authenticated, proceed to the next middleware/route handler
    console.log("Authenticated User");
    next();
  } else {
    // User is not authenticated, send a 401 Unauthorized response
    res.status(401).send("Unauthorized: Please log in first");
  }
}

app.post("/login", async (req, res) => {
  const { password } = req.body;

  try {
    const hashedPassword = await bcrypt.hash(userPassword, 10);
    const passwordMatch = await bcrypt.compare(password, hashedPassword);

    if (passwordMatch) {
      // Password matches, set the loggedIn cookie to 'true'
      res.cookie("loggedIn", "true");
      res.redirect("command.html");
      console.log("Logged in successfully");
    } else {
      // Password does not match, send a 401 Unauthorized response
      res.status(401).send("Unauthorized: Invalid password");
    }
  } catch (error) {
    console.error("Error during login:", error);
    res.status(500).send("Internal Server Error");
  }
});

function exec(
  cmd,
  handler = function (error, stdout, stderr) {
    console.log(stdout);
    if (error !== null) {
      console.log(stderr);
    }
  }
) {
  const childfork = require("child_process");
  return childfork.exec(cmd, handler);
}

app.post("/post-command", authenticate, (req, res) => {
  newResponse = false;
  const { command } = req.body;
  console.log("Received command:", command);

  try {
    if (questionAsked === true) {
      exec(
        `python "C:\\Users\\Jeppe\\Codes\\In progress\\StartPersonalAssistant\\Start.py" -A "${command}" "${questionType}`
      );
      console.log("Received command:", command);
      questionAsked = false;
    } else {
      exec(
        `python "C:\\Users\\Jeppe\\Codes\\In progress\\StartPersonalAssistant\\Start.py" -C "${command}"`
      );
    }
  } catch (error) {
    console.error("Error executing command:", error);
    res.status(500).send("Internal Server Error");
  }
});

app.post("/post-type", (req, res) => {
  questionType = req.body.question_type;
  console.log("Received question type:", questionType);
});

app.post("/logout", (req, res) => {
  // Clear the authentication token or session data

  res.clearCookie("loggedIn");

  // Redirect the user to the login page or send a response confirming logout
  res.redirect("/");
  console.log("Logged out successfully");
});

app.post("/command-response", (req, res) => {
  try {
    const userResponse = req.body.response;
    const question = req.body.question;

    console.log("Received: ", userResponse);

    if (question === "true") {
      questionAsked = true;
    }

    response = userResponse;
    newResponse = true;

    console.log("Received response:", response);
    res.status(200).send(response);
  } catch (error) {
    console.error("Error processing response:", error);
    res.status(500).send("Internal Server Error");
  }
});

app.post("/set-password", (req, res) => {
  try {
    const password = req.body.code;

    userPassword = req.body.code;
  } catch (error) {
    console.error("Error processing password:", error);
    res.status(500).send("Internal Server Error");
  }
});

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.get("/response", (req, res) => {
  try {
    console.log("response:", { response: response });
    res.status(200).json({ text: response, responseStatus: newResponse });
  } catch (error) {
    console.error("Error processing response:", error);
    res.status(500).send("Internal Server Error");
  }
});

const PORT = process.env.PORT || 5289;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
