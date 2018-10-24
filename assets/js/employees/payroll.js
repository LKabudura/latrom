import React, {Component} from 'react';
import {Heading, TableContent} from '../src/base_table';

export default class Payroll extends Component{
    render(){
        return(
            <div>
                <h3>Common Features</h3>
                <hr />
                <table>
                    <tbody>
                        <tr>
                            <th>Start Period</th>
                            <td>
                                <input className="form-control date" 
                                    type="text" 
                                    id="id_start_date"
                                    name="start-date" />
                            </td>
                        </tr>
                        <tr>
                            <th>End Period</th>
                            <td>
                                <input className="form-control date" 
                                    type="text"
                                    id="id_end_date" 
                                    name="end-date" />
                                </td>
                        </tr>
                    </tbody>
                </table>
                <hr />
                <h3>Payroll Table</h3>
                <hr />
                <PayrollTable  />
                </div>
            
        )
    }
}

class PayrollTable extends Component{
    constructor(props){
        super(props);
        this.state = {
            contents: [],
        }
    }

    addHandler(data){
        //request the full name from the api
        let new_contents = this.state.contents;
        new_contents.push(data);
        this.setState({contents: new_contents});
    }

    removeHandler(id){
        let newContents = this.state.contents;
        newContents.splice(id, 1);
        this.setState({contents: newContents});

    }
    reformatDate(date){
        var new_date = date.split('/');
        return(new_date[2] + '-' + new_date[0] + '-' + new_date[1]);
         
    }
    runPayroll(){
        console.log('run_payroll@');
        var i = 0;
        var data = this.state.contents;
        var start = $('#id_start_date').val();
        start = this.reformatDate(start);
        var stop = $('#id_end_date').val();
        stop = this.reformatDate(stop);
        var token = $('input[name=csrfmiddlewaretoken]').val();
        console.log(data);
        for( i in data){
            console.log(data[i].employee)
            $.ajax({
                url: '/employees/api/payslip/',
                method: 'POST',
                data: {
                    'csrfmiddlewaretoken': token,
                    'start_period': start,
                    'end_period': stop,
                    'employee': data[i].employee,
                    'normal_hours': data[i].normal_hours,
                    'overtime_one_hours': data[i].overtime_one_hours,
                    'overtime_two_hours': data[i].overtime_two_hours,
                    'pay_roll_id': 1
                },
                error: function(xhr, status, error){
                    console.log(status);
                    console.log(xhr.responseText);
                    console.log(error);
                },success: function(resp){
                    alert('Payroll run successfully');
                    window.location.replace('/employees/list-pay-slips');
                }
                
            });
        }
        
        
    }
    render(){
        var fields = ['employee', 'normal_hours', 'overtime_one_hours', 'overtime_two_hours'];
        var headings = ['Employee', 'Normal Time', 'Overtime', 'Overtime 2'];
        return(
            <div>
                <table>
                    <Heading fields={headings}/>
                    <TableContent contents={this.state.contents} 
                        subtotalHandler={(row)=>('')}
                        fields={fields}
                        removeHandler={this.removeHandler.bind(this)} />
                    <PayrollEntryRow addHandler={this.addHandler.bind(this)}/>
                </table>
                <hr className="my-4" />
                <button className="btn btn-success"
                    onClick={this.runPayroll.bind(this)}>
                
                Run Payroll</button>
            </div>
        )
    }
}

class PayrollEntryRow extends Component{
    constructor(props){
        super(props);
        this.state = {
            inputs: {
                'employee': '',
                'normal_hours': '',
                'overtime_one_hours': '',
                'overtime_two_hours': '',
            },
            employees: []
        }
    }

    resetInputs(){
        $('#id_employee').val("");
        $('#id_normal_hours').val("");
        $('#id_overtime_one_hours').val("");
        $('#id_overtime_two_hours').val("");
    }
    addHandler(){
        this.props.addHandler(this.state.inputs);
        this.setState({inputs: {
            'employee': '',
            'normal_hours': '',
            'overtime_one_hours': '',
            'overtime_two_hours': '',
        }})
        this.resetInputs()
    }
    componentDidMount(){
        //get list of employees
        $.ajax({
            'url': '/employees/api/employee/',
            'method': 'GET'
        }).then(res => {
            console.log(res);
            this.setState({employees:res});
        });
    }

    inputHandler(evt){
        var input = evt.target;
        var value = input.value;
        var new_inputs = this.state.inputs;
        new_inputs[input.name] = value;
        this.setState({inputs: new_inputs});

    }


    render(){
        return(
            <tfoot>
                <tr>
                <td></td>
                    <td>
                        <select className="form-control" 
                            name="employee"
                            id="id_employee"
                            onChange={this.inputHandler.bind(this)}>
                            <option value="">------</option>
                            {this.state.employees.map((e, key) =>(
                                <option value={e.employee_number} 
                                    key={key}>
                                    { e.first_name + " " + e.last_name}
                                </option>
                            ))}
                        </select>
                    </td>
                    <td><input className="form-control" 
                        name="normal_hours"
                        id="id_normal_hours" 
                        placeholder="Enter Time here..."
                        onChange={this.inputHandler.bind(this)} /></td>
                    <td><input className="form-control" 
                        name="overtime_one_hours"
                        id="id_overtime_one_hours" 
                        placeholder="Enter Time here..."
                        onChange={this.inputHandler.bind(this)} /></td>
                    <td><input className="form-control" 
                        name="overtime_two_hours"
                        id="id_overtime_two_hours" 
                        placeholder="Enter Time here..."
                        onChange={this.inputHandler.bind(this)} /></td>
                </tr>
                <tr>
                    <td colSpan={4}></td>
                    <td>
                        <button className="btn btn-primary pull-right"
                            onClick={this.addHandler.bind(this)}>
                                Add Employee</button>
                    </td>
                </tr>
            </tfoot>)
    }
}

