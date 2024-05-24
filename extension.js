// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "wally" is now active!');

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with  registerCommand
	// The commandId parameter must match the command field in package.json
	let disposable = vscode.commands.registerCommand('wally.helloWorld', async function () {
		// The code you place here will be executed every time your command is executed

		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from wally!');
		
		// make this extension open a file in project root directory named wally.json
		const fs = require('fs');
		const path = require('path');
		const rootPath = vscode.workspace.rootPath;
		const filePath = path.join(rootPath, 'wally.json');
		
		// read this json confiugration file and save it to a variable as json type
		let data
		try {
			data = fs.readFileSync(filePath, 'utf8');
		}
		catch (err) {
			console.error(err);
		}
		// parse the json data to a variable
		const jsonData = JSON.parse(data);
		console.log(jsonData);

		
	});

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
	activate,
	deactivate
}
