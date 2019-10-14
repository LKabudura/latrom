import React, {Component} from 'react';
import  ProductEntry from './entries/product'


class EntryWidget extends Component{
    state ={
        focused: "product",
        billables: [],
        inputs: {},
        
    }


    clickHandler = (evt) =>{
        this.setState({'focused': evt.target.id})
    }
    entryChangeHandler = (data) =>{
        //duplicates the state of the child elements
        this.setState({inputs: data})
    }


    insertHandler = () =>{
        if(!this.state.inputs.tax){
            alert('tax is required')
        }else if(!this.state.inputs.selected){
            alert('a valid choice must be selected')
        }else{
            const data = {
                type: this.state.focused,
                ...this.state.inputs
            }
            this.props.insertHandler(data)
            this.setState({inputs: {}})
        }
        
    }

    render(){
        const tabStyle = {
            listStyleType: 'none',
            display: 'inline-block',
            borderRadius: '5px 5px 0px 0px',
            padding: '5px',
            borderStyle: 'solid',
            borderColor: 'white'

        }

        const windowStyle = {
            width: '100%',
            padding: '5px',
            border: '0px 1px 1px 1px solid white',
        }
        return(
            <div style={{
                color: 'white',
                backgroundColor: '#007bff',
                padding: '5px'
            }}>
               
                <div className="entry-style">
                    <div style={{...windowStyle,
                        'display': this.state.focused === "product"
                            ?'block' 
                            :'none'
                        }}><ProductEntry
                                itemList={this.props.itemList} 
                                changeHandler={this.entryChangeHandler}     insertHandler={this.insertHandler}/></div>
                    
                </div>
            </div>
        )
    }
}


export default EntryWidget;