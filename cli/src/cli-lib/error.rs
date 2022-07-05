
use clap::Error as ClapError;


#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("There is an error with the cli: {0}")]
    CliError(#[from]  ClapError),
    #[error("Error while running the script: {0}")]
    ScriptError(String),
    #[error("Standard Input/Ouput error: {0}")]
    IoError(#[from] std::io::Error)
}



