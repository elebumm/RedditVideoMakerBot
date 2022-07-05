use crate::error::Error;
use std::process::Command;
use execute::Execute;
pub fn create_video() -> Result<(), Error> {
    let mut command = Command::new("python");
    command.arg("main.py");
    match command.execute_output() {
        Ok(o) => {
            println!("{}", String::from_utf8(o.stdout).unwrap())
        },
        Err(e) => {
            return Err(Error::ScriptError(e.to_string()))
        }
    }
    Ok(())
}