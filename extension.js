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
	let disposable = vscode.commands.registerCommand('wally.run', async function () {
		// The code you place here will be executed every time your command is executed

		// 1. make this extension open a file in project root directory named wally.json
		const fs = require('fs');
		const path = require('path');
		let rootPath = vscode.workspace.workspaceFolders[0].uri.fsPath;
		const filePath = path.join(rootPath, 'wally.json');
		
		if (rootPath[1] === ':') {
			rootPath = rootPath[0].toUpperCase() + rootPath.slice(1);
		}
		
		// 2. read this json confiugration file and save it to a variable as json type
		let data
		try {
			data = fs.readFileSync(filePath, 'utf8');
		}
		catch (err) {
			console.error(err);
		}
		
		// 3. parse the json data to a variable
		const jsonData = JSON.parse(data);
		console.log(jsonData);

		let target = jsonData.target;
		let unittest = jsonData.unit_test;
		let target_path = path.join(rootPath, jsonData.target);
		let unittest_path = path.join(rootPath, jsonData.unit_test);
		let tool = jsonData.tool;

		// Display a message box to the user
		vscode.window.showInformationMessage('Running wally on project <' + target + '> for <' + unittest + '> with testing tool <' + tool + '>.');

		// 4. execute the command
		// python3 ./wally-src/wally.py --target ./examples/maxify/maxify --unit-test ./examples/maxify/tests --runner pytest -m
		const extensionPath = context.extensionPath;
		const script = path.join(extensionPath, 'wally-src', 'wally.py');
		const exec = require('child_process').exec;
		const command = ['python', `${script}`, `--project-dir ${rootPath}`, `--target ${target_path}`, `--unit-test ${unittest_path}`, `--runner ${tool}`, '--save-mbfl-results', '--save-pre-analysis', '--show-mutants'].join(" ")
		exec(command, (err, stdout, stderr) => {
			if (err) {
				console.error(err);
				console.error(stderr);
				return;
			}
			console.log(stdout);
		});

		
	});

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
	activate,
	deactivate
}
