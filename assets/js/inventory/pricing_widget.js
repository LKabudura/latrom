import React, {Component} from "react";
import axios from "axios";

class PricingWidget extends Component{
    state = {
        selected: "0",
        markupValue: 0,
        directValue: 0,
        marginValue: 0
    }
    componentDidMount(){
        //check if update_page
        const URL = window.location.href;
        const URLelments = URL.split("/");
        const tail = URLelments[URLelments.length -1];
        if(tail !== "product-create"){
            axios({
                "method": "GET",
                "url": "/inventory/api/product/" + tail
            }).then(res =>{
                console.log(res.data.pricing_method)
                this.setState({
                    selected: toString(res.data.pricing_method),
                    marginValue: res.data.margin,
                    markupValue: res.data.markup,
                    directValue: res.data.direct_price
                })
            })
        }
    }

    radioHandler = (evt) =>{
        this.setState({selected: evt.target.value});
    }

    textInputHandler = (evt) =>{
        const name = evt.target.name;

        if(name === "direct_price"){
            this.setState({directValue: evt.target.value});
        }else if(name === "markup"){
            this.setState({markupValue: evt.target.value});
        }else{
            this.setState({marginValue: evt.target.value});
        }

    }
    render(){
        const cellStyle = {
            padding: "10px"
        };
        const readOnlyStyle = {
            backgroundColor: "#ddd",
            border: "1px solid #aaa"
        }
        return(
            <div style={{width: "100%"}}>
                <div style={{margin:"0px auto", width:"300px"}}>
                    <table>
                        <thead>
                            <tr>
                                <th className="bg-primary text-white" 
                                    style={cellStyle}>Pricing Method</th>
                                <th className="bg-primary text-white" 
                                    style={cellStyle}>Value</th>
                            </tr>
                        </thead>
                        <thead>
                            <tr>
                                <td>
                                    <label>
                                        <input type="radio" 
                                            name="pricing_method"
                                            value={0}
                                            checked={this.state.selected === "0"}
                                            onChange={this.radioHandler} />
                                        Direct
                                    </label>
                                </td>
                                <td>
                                    <input type="number"
                                        style={this.state.selected === "0" ? null: readOnlyStyle} 
                                        name="direct_price"
                                        value={this.state.directValue}
                                        onChange={this.textInputHandler}
                                        readOnly={!(this.state.selected === "0")}/>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <label>
                                        <input type="radio" 
                                            name="pricing_method" 
                                            value={1}
                                            checked={this.state.selected === "1"}
                                            onChange={this.radioHandler}
                                                />
                                        Margin
                                    </label>
                                </td>
                                <td>
                                    <input type="number" 
                                        name="margin"
                                        onChange={this.textInputHandler}
                                        value={this.state.marginValue}
                                        style={this.state.selected === "1" ? null: readOnlyStyle}
                                        readOnly={!(this.state.selected === "1")}/>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <label>
                                        <input type="radio" 
                                            name="pricing_method" 
                                            value={2}
                                            checked={this.state.selected === "2"}
                                            onChange={this.radioHandler}/>
                                        Markup
                                    </label>
                                </td>
                                <td>
                                    <input type="number" 
                                        name="markup"
                                        style={this.state.selected === "2" ? null: readOnlyStyle}
                                        value={this.state.markupValue}
                                        onChange={this.textInputHandler}
                                        readOnly={!(this.state.selected === "2")}/>
                                </td>
                            </tr>
                        </thead>
                    </table>
                </div>
            </div>
        )
    }
}

export default PricingWidget;