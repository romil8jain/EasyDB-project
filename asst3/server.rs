/*
 * server.rs
 *
 * Implementation of EasyDB database server
 *
 * University of Toronto
 * 2019
 */

use std::net::TcpListener;
use std::net::TcpStream;
use std::io::Write;
use std::io;
use packet::Command;
use packet::Response;
use packet::Network;
use schema::Table;
use database;
use database::Database;
use std::thread; 
use std::sync::Arc;
use std::sync::Mutex; 


// fn single_threaded(listener: TcpListener, table_schema: Vec<Table>, verbose: bool)
// {

//     let mut db = Database::new(table_schema);

//     for stream in listener.incoming() {
//         let stream = stream.unwrap();
        
//         if verbose {
//             println!("Connected to {}", stream.peer_addr().unwrap());
//         }
        
//         // The infinite loop of listening starts here until it is disconnected
//         match handle_connection(stream, &mut db) {
//             Ok(()) => {
//                 if verbose {
//                     println!("Disconnected.");
//                 }
//             },
//             Err(e) => eprintln!("Connection error: {:?}", e),
//         };
//     }
// }

fn multi_threaded(listener: TcpListener, table_schema: Vec<Table>, verbose: bool)
{
    let mut db = Arc::new(Mutex::new(Database::new(table_schema)));

    //runs in an infinite loop and keeps listening for connections
    for stream in listener.incoming() {
        let stream = stream.unwrap();
        
        if verbose {
            println!("Connected to {}", stream.peer_addr().unwrap());
        }
        
        let db = db.clone(); //clone the arc to be moved in the thread
        let th = std::thread::spawn(move || {
            // The infinite loop of listening starts here until it is disconnected
            match handle_connection(stream, &db) {
                Ok(()) => {
                    if verbose {
                        println!("Disconnected.");
                    }
                },
                Err(e) => eprintln!("Connection error: {:?}", e),
            };
            let mut db = db.lock().unwrap();
            (*db).num_conn -=1;
        });

        th.join().unwrap();
    }
}

/* Sets up the TCP connection between the database client and server */
pub fn run_server(table_schema: Vec<Table>, ip_address: String, verbose: bool)
{
    let listener = match TcpListener::bind(ip_address) {
        Ok(listener) => listener,
        Err(e) => {
            eprintln!("Could not start server: {}", e);
            return;
        },
    };
    
    println!("Listening: {:?}", listener);
    
    /*
     * TODO: replace with multi_threaded
     */
    multi_threaded(listener, table_schema, verbose);
}

impl Network for TcpStream {}

/* Receive the request packet from ORM and send a response back */
fn handle_connection(mut stream: TcpStream, db_send: & Arc<Mutex<Database>>) 
    -> io::Result<()> 
{
    /* 
     * Tells the client that the connction to server is successful.
     * TODO: respond with SERVER_BUSY when attempting to accept more than
     *       4 simultaneous clients.
     */
    
    let mut db = db_send.lock().unwrap();
    (*db).num_conn +=1;
    if (*db).num_conn >=4 {
        stream.respond(&Response::Error(Response::SERVER_BUSY));
        return Err(io::Error::new(io::ErrorKind::Other,
            "Server Busy"));
    }
    else{
        stream.respond(&Response::Connected)?;
    }

    drop(db);
    loop {
        let request = match stream.receive() {
            Ok(request) => request,
            Err(e) => {
                /* respond error */
                stream.respond(&Response::Error(Response::BAD_REQUEST))?;
                return Err(e);
            },
        };
        
        /* we disconnect with client upon receiving Exit */
        if let Command::Exit = request.command {
            break;
        }
        
        /* Send back a response */
        let response = database::handle_request(request, db_send); // db is borrowed by handle_request
        
        stream.respond(&response)?;
        stream.flush()?;
    }

    Ok(())
}

