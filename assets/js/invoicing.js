import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import Invoice from './invoices/invoice';
import MutableTable from './src/mutable_table/container/root';

const creditNote = document.getElementById('credit-note-table');
const directPurchase =  document.getElementById('direct-purchase-table');
const sales = document.getElementById('invoice-table')

const URL = window.location.href;
const  decomposed = URL.split('/');
const tail = decomposed[decomposed.length - 1];
    
if(sales){
    ReactDOM.render(<Invoice />, sales);
}else if(creditNote){
    let decomposedURL = window.location.href.split('/');
    let pk = decomposedURL[decomposedURL.length - 1];
    ReactDOM.render(<MutableTable 
        dataURL={'/invoicing/api/sales-invoice/' + pk}
        headings={["Product", "Invoiced Quantity", "Unit Price", "Returned Quantity"]}
        resProcessor={(res) =>{
            // filter by lines which have a returned value less than 1
            return res.data.salesinvoiceline_set.map((line, i)=>({
                product: line.id + " - " +line.product.name,
                quantity: line.quantity,
                unit_price: line.product.unit_sales_price,
                returned_quantity: line.returned_quantity
            }))
        }}
        fields={[
            {'name': 'product', 'mutable': false},
            {'name': 'quantity', 'mutable': false},
            {'name': 'unit_price', 'mutable': false},
            {'name': 'returned_quantity', 'mutable': true},
        ]}
        formHiddenFieldName="returned-items"
        />, creditNote)
}else if(directPurchase){
    ReactDOM.render(<PurchaseTable />, directPurchase);
}
