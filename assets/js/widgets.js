import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import TreeSelectWidget from '../js/src/tree_select_widget';
import axios from 'axios';
import MessageDetail from '../js/messaging/container/root';
import PricingWidget from "../js/inventory/pricing_widget";
import InvoiceTable from '../js/invoices/invoice';
import EmailEditor from '../js/messaging/components/rich_text';


const storageMedia = document.getElementById('storage-media-select-widget');
const category = document.getElementById('category-select-widget');
const categoryView = document.getElementById('category-tree-view');
const storageMediaView = document.getElementById('storage-media-tree-view');
const threadView = document.getElementById('thread-widget');
const testView = document.getElementById('test');
const pricing = document.getElementById('pricing-widget');
const rich_text = document.getElementById('message-field');
const depts = document.getElementById('department-list');
const dataMapper = (node, i) =>{
    
    return({
        label: node.name,
        nodes: node.children,
        id: node.id
    });
}

const currentWarehouse = () =>{
    let decomposed = window.location.href.split('/');
    return(decomposed[decomposed.length-1])
}
if(storageMedia){
    const pk = currentWarehouse();
    axios.get('/inventory/api/storage-media-detail/' + pk).then(
        res => {
            ReactDOM.render(<TreeSelectWidget 
                url={'/inventory/api/storage-media-nested/' + res.data.warehouse}
                externalFormFieldName='location'
                updateUrlRoot='/inventory/storage-media-update/'
                detailUrlRoot='/inventory/storage-media-detail/'
                dataMapper={dataMapper}/>, storageMedia);
        }
    )
    
}else if(category){
    ReactDOM.render(<TreeSelectWidget 
        url='/inventory/api/category'
        externalFormFieldName='parent'
        dataMapper={dataMapper}/>, category);
}else if(categoryView){
    ReactDOM.render(<TreeSelectWidget 
        isListView={true}
        updateUrlRoot='/inventory/category-update/'
        detailUrlRoot='/inventory/category-detail/'
        url='/inventory/api/category'
        externalFormFieldName='parent'
        dataMapper={dataMapper}/>, categoryView);
}else if(storageMediaView){
    let pk = currentWarehouse();
    ReactDOM.render(<TreeSelectWidget
        isListView={true} 
        url={'/inventory/api/storage-media-nested/' + pk}
        externalFormFieldName='location'
        updateUrlRoot='/inventory/storage-media-update/'
        detailUrlRoot='/inventory/storage-media-detail/'
        dataMapper={dataMapper}/>, storageMediaView);
}else if(threadView){
    ReactDOM.render(<MessageDetail />, threadView);
}else if(testView){
    ReactDOM.render(<InvoiceTable itemList={[]} />, testView);
}else if(pricing){
    ReactDOM.render(<PricingWidget />, pricing);
}else if(depts){
    ReactDOM.render(<TreeSelectWidget 
        isListView={true}
        updateUrlRoot='/employees/department/update/'
        detailUrlRoot='/employees/department/detail/'
        url='/employees/api/department'
        externalFormFieldName='parent_department'//not important
        dataMapper={dataMapper}/>, depts);
}else if(rich_text){
    console.log('rich');
    ReactDOM.render(<EmailEditor />, rich_text);
}
