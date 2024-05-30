// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

function getColor(suspiciousness) {
	// the suspiciousness is in the range of [-1, 1]

	if (suspiciousness >= 0) {
		// red
		const red = 255;
		const green = 0;
		const blue = 0;
		const alpha = Math.abs(suspiciousness);
		return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
	} else {
		// green
		const red = 0;
		const green = 255;
		const blue = 0;
		const alpha = Math.abs(suspiciousness);
		return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
	}
}


/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('"wally" is now active!');
	// initialize storage for suspiciousness hovering
	const hoverSuspiciousnessKey = 'wally.hoverSuspiciousness';
	context.workspaceState.update(hoverSuspiciousnessKey, []);

	function wally_mbfl(callback) {
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
		console.log(extensionPath);
		const script = path.join(extensionPath, 'wally-src', 'wally.py');
		const exec = require('child_process').exec;
		const command = ['python', `${script}`, `--project-dir ${rootPath}`, `--target ${target_path}`, `--unit-test ${unittest_path}`, `--runner ${tool}`, `--working-dir ${extensionPath}`, '--save-mbfl-results', '--save-pre-analysis', '--show-mutants'].join(" ")

		exec(command, (err, stdout, stderr) => {
			if (err) {
				console.error(err);
				console.error(stderr);
				vscode.window.showErrorMessage('Wally failed to run. Please check the output for more information.');
				vscode.window.showErrorMessage(err);
				vscode.window.showErrorMessage(stderr);
				return;
			}
			console.log(stdout);
			callback();
		});
	}


	function highlightLine() {
		// dispose the all hoverSuspiciousness
		const hovers = context.workspaceState.get(hoverSuspiciousnessKey);
		for (let hover of hovers) {
			hover.dispose();
		}
		context.workspaceState.update(hoverSuspiciousnessKey, []);


		const fs = require('fs');
		const path = require('path');
		const extensionPath = context.extensionPath;
		// 5. read mbfl_results.json
		const mbfl_results_path = path.join(extensionPath, 'mbfl_results.json');
		let mbfl_results_data
		try {
			mbfl_results_data = fs.readFileSync(mbfl_results_path, 'utf8');
		}
		catch (err) {
			console.error(err);
			vscode.window.showErrorMessage('Wally is not run yet. Please run/wait Wally first.');
		}
		const mbfl_results_json = JSON.parse(mbfl_results_data);

		// 6. get the suspiciousness of each line of each file
		// {file_path: "lines": {"6": {"suspiciousness": 0.5}}, ...}
		let suspiciousness = {};
		for (let file_path in mbfl_results_json) {
			suspiciousness[file_path] = {};
			for (let line in mbfl_results_json[file_path]['lines']) {
				let suspiciousness_value = mbfl_results_json[file_path]['lines'][line]['suspiciousness'];
				suspiciousness[file_path][line] = suspiciousness_value;
			}
		}

		const editor = vscode.window.activeTextEditor;
		let decorationType = vscode.window.createTextEditorDecorationType({})
		if (editor) {
			const document = editor.document;
			const lineCount = document.lineCount;

			editor.setDecorations(decorationType, [])
			decorationType.dispose();

			let decorations = [];
			for (let file_path in suspiciousness) {
				let lower_file_path = ""
				if (file_path[1] === ':') {
					lower_file_path = file_path[0].toLowerCase() + file_path.slice(1);
				}
				if (document.fileName.includes(lower_file_path)) {
					for (let line in suspiciousness[file_path]) {
						const suspiciousness_value = suspiciousness[file_path][line];
						const line_number = parseInt(line) - 1;
						const range = new vscode.Range(line_number, 0, line_number, 1);

						const color = getColor(suspiciousness_value);

						// highlight the line
						editor.setDecorations(
							vscode.window.createTextEditorDecorationType({
								isWholeLine: true,
								backgroundColor: color,
							}),
							[range]
						);

						// show suspciiousness value when hover
						context.workspaceState.get(hoverSuspiciousnessKey).push(
							vscode.languages.registerHoverProvider('*', {
								provideHover(document, position, token) {
									if (position.line === line_number && document.fileName.includes(file_path)) {
										return new vscode.Hover(`Suspiciousness score: ${suspiciousness_value}`);
									}
									return null;
								}
							})
						);
					}
				}
			}
		}
	}

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with  registerCommand
	// The commandId parameter must match the command field in package.json
	let disposable = vscode.commands.registerCommand('wally.run', async function () {
		context.hoverSuspiciousness = new Array();
		wally_mbfl(() => {
			highlightLine();
			vscode.window.onDidChangeActiveTextEditor(highlightLine);
		});
	});
	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
function deactivate() { }

module.exports = {
	activate,
	deactivate
}
