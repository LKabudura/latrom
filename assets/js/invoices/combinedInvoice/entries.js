import React, {Component} from 'react';
import {SearchableWidget} from '../../src/common';

const inlineStyles = {
    display: "inline",
    float: "left"
};

class ServiceEntry extends Component{
    state = {
        hours: 0
    }
    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                hours: 0
            })
            //remove selected choice from list of choices 
        }
    }

    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                hours: 0
            })
            //remove selected choice from list of choices 
        }
    }

    handler = (evt) =>{
        this.setState({hours: evt.target.value})
        this.props.onChangeHours(evt);
    }


    render(){
        
        return(
            <div>
                <div style={{...inlineStyles, width:"70%"}}>
                    <SearchableWidget
                        list={this.props.itemList}
                        dataURL="/services/api/service/"
                        displayField="name"
                        idField="id"
                        onSelect={this.props.onSelect}
                        onClear={this.props.onClear} />
                </div>
                <div style={{...inlineStyles, width:"30%"}}>
                    <input 
                        type="number"
                        placeholder="Hours..."
                        className="form-control"
                        value={this.state.hours}
                        onChange={this.handler}/>
                </div>
            </div>
        )
    };
}
    

class ProductEntry extends Component{
    state = {
        quantity: 0
    }

    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                quantity: 0
            })
            //remove selected choice from list of choices 
        }
    }

    handler = (evt) =>{
        console.log(evt.target.value);
        if(evt.target.value && evt.target.value > 0){
            this.setState({quantity: evt.target.value})
            this.props.onChangeQuantity(evt);
        }else{
            alert("Please select a valid value greater than 0");
        }
        
    }

    render(){
        return(
            <div>
                <div style={{...inlineStyles, width:"70%"}}>
                    <SearchableWidget
                        list={this.props.itemList}
                        dataURL="/inventory/api/product/"
                        displayField="name"
                        idField="id"
                        onSelect={this.props.onSelect}
                        onClear={this.props.onClear} />
                </div>
                <div style={{...inlineStyles, width:"30%"}}>
                    <input 
                        type="number"
                        value={this.state.quantity}
                        placeholder="Quantity..."
                        className="form-control"
                        onChange={this.handler}/>
                </div>
            </div>
            )
    }
}

const BillableEntry = (props) => {
    if(props.billables.length === 0){
            return(
                <div>
                    <center>
                        <h6>The selected customer has no billables</h6>
                    </center>
                </div>
            )
        }else{
            return(
                <div style={{width:"100%"}}>
                    <input 
                        type="text"
                        className="form-control"
                        list="billable_datalist"
                        placeholder="Select Billable Expense..."
                        onChange={props.inputHandler} />
                    <datalist id="billable_datalist">
                        {props.billables.map((billable, i)=>(
                            <option key={i}>
                                {billable.id + '-' + billable.description}
                            </option>
                        ))}
                    </datalist>
                </div>
            )
        }
};

export {ServiceEntry, BillableEntry, ProductEntry};