use clap::Command;
use commands::create_video;
use error::Error;

pub mod commands;
pub mod error;

pub struct Cli;

impl Cli {
    pub fn start() -> Result<(), Error> {
        let app = Command::new("reddit-video-maker")
            .about("Create Reddit Videos with \u{2728} one command \u{2728}")
            .subcommand(
            Command::new("create").about("Start the process of creating the video")
            );
        let matches = app.clone().get_matches();
        match matches.subcommand() {
            Some(("create", _)) => {
                create_video()?;
            },
            Some(_) => {
                app.clone().print_help()?;
            }
            None => {
                app.clone().print_help()?;
            }
        }
        Ok(())
    }
}
