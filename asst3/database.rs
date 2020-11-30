/*
 * database.rs
 *
 * Implementation of EasyDB database internals
 *
 * University of Toronto
 * 2019
 */

use packet::{Command, Request, Response, Value};
use schema::Table;
use std::sync::Mutex; 
use std::sync::Arc;
 
/* OP codes for the query command */
pub const OP_AL: i32 = 1;
pub const OP_EQ: i32 = 2;
pub const OP_NE: i32 = 3;
pub const OP_LT: i32 = 4;
pub const OP_GT: i32 = 5;
pub const OP_LE: i32 = 6;
pub const OP_GE: i32 = 7;

/* You can implement your Database structure here
 * Q: How you will store your tables into the database? */
pub struct Database { 
    pub Tables: Vec<Table>,
    pub num_conn: i32,
}

impl Database {
    pub fn new(tables: Vec<Table>) -> Database{
        Database{
            Tables: tables,
            num_conn: 0,
        }
    }
}

/* Receive the request packet from client and send a response back */
pub fn handle_request(request: Request, db: & Arc<Mutex<Database>>) 
    -> Response  
{           
    /* Handle a valid request */
    let result = match request.command {
        Command::Insert(values) => 
            handle_insert(db, request.table_id, values),
        Command::Update(id, version, values) => 
             handle_update(db, request.table_id, id, version, values),
        Command::Drop(id) => handle_drop(db, request.table_id, id),
        Command::Get(id) => handle_get(db, request.table_id, id),
        Command::Query(column_id, operator, value) => 
            handle_query(db, request.table_id, column_id, operator, value),
        /* should never get here */
        Command::Exit => Err(Response::UNIMPLEMENTED),
    };
    
    /* Send back a response */
    match result {
        Ok(response) => response,
        Err(code) => Response::Error(code),
    }
}

/*
 * TODO: Implment these EasyDB functions
 */
 
#[allow(non_snake_case)]
fn handle_insert(db: & Arc<Mutex<Database>>, table_id: i32, values: Vec<Value>) 
    -> Result<Response, i32> 
{
    
    let mut db = db.lock().unwrap();

    if table_id as usize > (*db).Tables.len() || table_id == 0{
        return Err(Response::BAD_TABLE); 
    }

    let Table_id = table_id -1; 

    // check if column length and values length is same
    if (*db).Tables[Table_id as usize].t_cols.len() != values.len(){
        return Err(Response::BAD_ROW);
    }

    // Increase value of rows
    (*db).Tables[Table_id as usize].t_pk+= 1; 
    let t_pk = (*db).Tables[Table_id as usize].t_pk;

    // Error checking in columns to check if passed values matches schema
    for i in 0..values.len(){
        match &values[i]{
            Value:: Integer(val) => {
                if (*db).Tables[Table_id as usize].t_cols[i].c_type != Value::INTEGER{
                    return Err(Response::BAD_VALUE);
                }
            },
            Value:: Float(val) => {
                if (*db).Tables[Table_id as usize].t_cols[i].c_type != Value::FLOAT{
                    return Err(Response::BAD_VALUE);
                }
            },
            Value:: Text(val) => {
                if (*db).Tables[Table_id as usize].t_cols[i].c_type != Value::STRING{
                    return Err(Response::BAD_VALUE);
                }
            },
            Value:: Foreign(val) => {
                if (*db).Tables[Table_id as usize].t_cols[i].c_type != Value::FOREIGN{
                    return Err(Response::BAD_VALUE);
                }

                let foreign_table_id = (*db).Tables[Table_id as usize].t_cols[i].c_ref -1;

                match (*db).Tables[foreign_table_id as usize].t_values.get(&val){
                    None => return Err(Response::BAD_FOREIGN),
                    _ => {}
                }

                // problem: remember I am pushing the same kind of table_id here that a user may push
                (*db).Tables[foreign_table_id as usize].t_foreign_refs.push((table_id, t_pk)); 
                
            },
            _ => println!("Shouldnt have reached here"),
        }
    }

    (*db).Tables[Table_id as usize].t_values.insert(t_pk, (1, values));
    return Ok(Response::Insert(t_pk, 1));
}

//get_mut method of hashmap
fn handle_update(db: & Arc<Mutex<Database>>, table_id: i32, object_id: i64, 
    version: i64, values: Vec<Value>) -> Result<Response, i32> 
{

    let mut db = db.lock().unwrap();

    if table_id as usize > (*db).Tables.len() || table_id == 0{
        return Err(Response::BAD_TABLE); // problem: mostly works correctly
    }

    let Table_id = table_id -1; // problem: mostly works correctly

    // check if column length and values length is same
    if (*db).Tables[Table_id as usize].t_cols.len() != values.len(){
        return Err(Response::BAD_ROW);
    }


    for i in 0..values.len(){
        match &values[i]{
            Value:: Integer(val) => {
                if (*db).Tables[Table_id as usize].t_cols[i].c_type != Value::INTEGER{
                    return Err(Response::BAD_VALUE);
                }
            },
            Value:: Float(val) => {
                if (*db).Tables[Table_id as usize].t_cols[i].c_type != Value::FLOAT{
                    return Err(Response::BAD_VALUE);
                }
            },
            Value:: Text(val) => {
                if (*db).Tables[Table_id as usize].t_cols[i].c_type != Value::STRING{
                    return Err(Response::BAD_VALUE);
                }
            },
            Value:: Foreign(val) => {
                if (*db).Tables[Table_id as usize].t_cols[i].c_type != Value::FOREIGN{
                    return Err(Response::BAD_VALUE);
                }

                let foreign_table_id = (*db).Tables[Table_id as usize].t_cols[i].c_ref -1;

                match (*db).Tables[foreign_table_id as usize].t_values.get(&val){
                    None => return Err(Response::BAD_FOREIGN),
                    _ => {}
                }

                // problem: remember I am pushing the same kind of table_id here that a user may push
                (*db).Tables[foreign_table_id as usize].t_foreign_refs.push((table_id.clone(), object_id.clone())); 
            },
            _ => println!("Shouldnt have reached here"),
        }
    }
    
    let mut version_returned:i64;
    match (*db).Tables[Table_id as usize].t_values.get(&object_id){
        Some(returned_tup) => version_returned = returned_tup.0 + 1,
        None => return Err(Response::NOT_FOUND),
    };


    if version == 0 {
        (*db).Tables[Table_id as usize].t_values.insert(object_id, (version_returned, values));
        return Ok(Response::Update(version_returned));
    }
    if version_returned != version+1{
        return Err(Response::TXN_ABORT);
    }

    (*db).Tables[Table_id as usize].t_values.insert(object_id, (version +1, values));
    return Ok(Response::Update(version +1));
    
}

fn handle_drop(db_send: & Arc<Mutex<Database>>, table_id: i32, object_id: i64) 
    -> Result<Response, i32>
{
    let mut db = db_send.lock().unwrap();

    if table_id as usize > (*db).Tables.len() || table_id == 0{
        return Err(Response::BAD_TABLE); // problem: mostly works correctly
    }

    let Table_id = table_id - 1;

    match (*db).Tables[Table_id as usize].t_values.get(&object_id){
        None => return Err(Response::NOT_FOUND),
        _ => {},
    };

    // delete all rows in other tables that were referencing this row
    for i in 0..(*db).Tables[Table_id as usize].t_foreign_refs.len(){
        let foreign_ref1 = (*db).Tables[Table_id as usize].t_foreign_refs[i].0;
        let foreign_ref2 = (*db).Tables[Table_id as usize].t_foreign_refs[i].1;
        drop(db);
        handle_drop(db_send, foreign_ref1, foreign_ref2);
        db = db_send.lock().unwrap();
    }    

    // remove the foreign_ref from the table that it was referencing
    // for i in 0..db.Tables[Table_id as usize].t_cols.len(){
    //     if db.Tables[Table_id as usize].t_cols[i].c_type == Value::FOREIGN {
    //         let foreign_table_id = db.Tables[Table_id as usize].t_cols[i].c_ref - 1;

    //         if let Some(pos) = db.Tables[foreign_table_id as usize].t_foreign_refs.iter().position(|x| *x == (table_id, object_id)) {
    //             db.Tables[foreign_table_id as usize].t_foreign_refs.remove(pos);
    //         }
    //     }
    // }

    (*db).Tables[Table_id as usize].t_values.remove(&object_id);
    return Ok(Response::Drop);
}

#[allow(non_snake_case)]
fn handle_get(db: & Arc<Mutex<Database>>, table_id: i32, object_id: i64) 
    -> Result<Response, i32>
{
    let mut db = db.lock().unwrap();

    if table_id as usize > (*db).Tables.len() || table_id == 0{
        return Err(Response::BAD_TABLE); // problem: mostly works correctly
    }

    let Table_id = table_id - 1;
    match (*db).Tables[Table_id as usize].t_values.get(&object_id){
        Some(returned_tup) => return Ok(Response::Get(returned_tup.0, returned_tup.1.clone())),
        None => return Err(Response::NOT_FOUND),
    };

    // return Ok(Response::Get(*version, &vec_values));
}

fn handle_query(db: & Arc<Mutex<Database>>, table_id: i32, column_id: i32,
    operator: i32, other: Value) 
    -> Result<Response, i32>
{
    let mut db = db.lock().unwrap();

    let Table_id = table_id - 1;
    let Column_id = column_id - 1;
    let mut list: Vec<i64> = Vec::new();

    if table_id as usize > (*db).Tables.len() || table_id == 0{
        return Err(Response::BAD_TABLE); // problem: mostly works correctly
    }

    if column_id as usize > (*db).Tables[Table_id as usize].t_cols.len(){
        return Err(Response::BAD_QUERY); // problem: mostly works correctly
    }

    if operator == OP_AL && column_id !=0 {
        return Err(Response::BAD_QUERY);
    }

    // OP_AL column field ignored
    if operator == OP_AL{
        for (key, somevalue) in &(*db).Tables[Table_id as usize].t_values {
            list.push(*key);
        }
        return Ok(Response::Query(list));
    }

    match &other{
        Value:: Integer(val) => {
            if (*db).Tables[Table_id as usize].t_cols[Column_id as usize].c_type != Value::INTEGER{
                return Err(Response::BAD_QUERY);
            }
        },
        Value:: Float(val) => {
            if (*db).Tables[Table_id as usize].t_cols[Column_id as usize].c_type != Value::FLOAT{
                return Err(Response::BAD_QUERY);
            }
        },
        Value:: Text(val) => {
            if (*db).Tables[Table_id as usize].t_cols[Column_id as usize].c_type != Value::STRING{
                return Err(Response::BAD_QUERY);
            }
        },
        Value:: Foreign(val) => {
            if (*db).Tables[Table_id as usize].t_cols[Column_id as usize].c_type != Value::FOREIGN{
                return Err(Response::BAD_QUERY);
            }
        },
        _ => return Err(Response::BAD_QUERY),
    }

    if (*db).Tables[Table_id as usize].t_cols[Column_id as usize].c_type == Value::FOREIGN || column_id == 0 {
        let foreign_id = match other {
            Value::Foreign(f) => f,
            _ =>  0,
        };

        match operator {
            OP_EQ => {
                for (key, val) in (*db).Tables[Table_id as usize].t_values.iter() {
                    if column_id == 0 && *key == foreign_id{
                        list.push(*key);
                    }
                    else if val.1[Column_id as usize] == other{
                        list.push(*key);
                    }
                }
            },
            OP_NE => {
                for (key, val) in (*db).Tables[Table_id as usize].t_values.iter() {
                    if column_id == 0 && *key != foreign_id{
                        list.push(*key);
                    }
                    else if val.1[Column_id as usize] != other{
                        list.push(*key);
                    }
                }
            },
            _ => return Err(Response::BAD_QUERY),
        }
        return Ok(Response::Query(list));
    }

    match operator {
        OP_GE => {
            for (key, val) in (*db).Tables[Table_id as usize].t_values.iter() {
                if val.1[Column_id as usize] >= other {
                    list.push(*key);
                }
            }
        }
        OP_GT => {
            for (key, val) in (*db).Tables[Table_id as usize].t_values.iter() {
                if val.1[Column_id as usize] > other {
                    list.push(*key);
                }
            }
        }
        OP_LE => {
            for (key, val) in (*db).Tables[Table_id as usize].t_values.iter() {
                if val.1[Column_id as usize] <= other {
                    list.push(*key);
                }
            }
        }
        OP_LT => {
            for (key, val) in (*db).Tables[Table_id as usize].t_values.iter() {
                if val.1[Column_id as usize] < other {
                    list.push(*key);
                }
            }
        }
        OP_EQ => {
            for (key, val) in (*db).Tables[Table_id as usize].t_values.iter() {
                if val.1[Column_id as usize] == other{
                    list.push(*key);
                }
            }
        },
        OP_NE => {
            for (key, val) in (*db).Tables[Table_id as usize].t_values.iter() {
                if val.1[Column_id as usize] != other{
                    list.push(*key);
                }
            }
        },
        _ => return Err(Response::BAD_QUERY),
    }
    return Ok(Response::Query(list));
}


