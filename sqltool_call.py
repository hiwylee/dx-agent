import asyncio
import os
from dotenv import load_dotenv
from oci.addons.adk import Agent, AgentClient

from oci.addons.adk.run.types import InlineInputLocation, ObjectStorageInputLocation
from oci.addons.adk.tool.prebuilt.agentic_sql_tool import AgenticSqlTool, SqlDialect, ModelSize

# Load environment variables from .env file
load_dotenv()


INLINE_TABLE_DESC = """
"AP_HOLDS_ALL"."INVOICE_ID"  'Invoice identifier ';
"AP_HOLDS_ALL"."LINE_LOCATION_ID"  'Purchase order line location identifier ';
"AP_HOLDS_ALL"."HOLD_LOOKUP_CODE"  'Name of hold code ';
"AP_HOLDS_ALL"."LAST_UPDATE_DATE"  'Standard Who column ';
"AP_HOLDS_ALL"."LAST_UPDATED_BY"  'Standard Who column ';
"AP_HOLDS_ALL"."HELD_BY"  'User that placed hold on invoice ';
"AP_HOLDS_ALL"."HOLD_DATE"  'Date user placed hold on invoice ';
"AP_HOLDS_ALL"."HOLD_REASON"  'Reason for hold being placed on invoice ';
"AP_HOLDS_ALL"."RELEASE_LOOKUP_CODE"  'Name of release code ';
"AP_HOLDS_ALL"."RELEASE_REASON"  'Reason for release being placed on invoice ';
"AP_HOLDS_ALL"."STATUS_FLAG"  'No longer used ';
"AP_HOLDS_ALL"."LAST_UPDATE_LOGIN"  'Standard Who column ';
"AP_HOLDS_ALL"."CREATION_DATE"  'Standard Who column ';
"AP_HOLDS_ALL"."CREATED_BY"  'Standard Who column ';
"AP_HOLDS_ALL"."ATTRIBUTE_CATEGORY"  'Descriptive Flexfield structure defining columns ';
"AP_HOLDS_ALL"."ORG_ID"  'Organization identifier ';
"AP_HOLDS_ALL"."RESPONSIBILITY_ID"  'Responsibility identifier associated with Insufficient Funds hold ';
"AP_HOLDS_ALL"."RCV_TRANSACTION_ID"  'Receipt identifier, RCV_TRANSACTIONS.TRANSACTION_ID, of receipt that th hold  assoicated with ';
"""

INLINE_ICL_EXAMPLES = """
Question: get invoice holding list
Oracle SQL: 
SELECT
    aha.INVOICE_ID,
    aha.LINE_LOCATION_ID,
    aha.HOLD_LOOKUP_CODE,
    aha.LAST_UPDATE_DATE,
    aha.LAST_UPDATED_BY,
    aha.HELD_BY,
    aha.HOLD_DATE,
    aha.HOLD_REASON,
    aha.RELEASE_LOOKUP_CODE,
    aha.RELEASE_REASON,
    aha.ORG_ID,
    aha.RESPONSIBILITY_ID,
    aha.RCV_TRANSACTION_ID,
    aha.HOLD_DETAILS,
    aha.LINE_NUMBER,
    aha.HOLD_ID,
    aha.WF_STATUS,
    aha.VALIDATION_REQUEST_ID
FROM ap_holds_all aha
WHERE 1 = 1
  AND aha.HOLD_LOOKUP_CODE IN ('QTY ORD', 'QTY REC', 'PRICE', 'AMT ORG');


Question: list invoice details info for invoice_id='346843' 
Oracle SQL: 
select aia.*
from ap_invoices_all aia,
          ap_holds_all aha
where 1=1
and aia.invoice_id = aha.invoice_id
and aha.HOLD_LOOKUP_CODE in ('QTY ORD', 'QTY  REC', 'PRICE', 'AMT ORG')
and aha.INVOICE_ID='346843' ;

"""

INLINE_DATABASE_SCHEMA = """
CREATE TABLE APPS.AP_HOLDS_ALL
   (	"INVOICE_ID" NUMBER(15,0), 
	"LINE_LOCATION_ID" NUMBER(15,0), 
	"HOLD_LOOKUP_CODE" VARCHAR2(25 BYTE), 
	"LAST_UPDATE_DATE" DATE, 
	"LAST_UPDATED_BY" NUMBER(15,0), 
	"HELD_BY" NUMBER(15,0), 
	"HOLD_DATE" DATE, 
	"HOLD_REASON" VARCHAR2(240 BYTE), 
	"RELEASE_LOOKUP_CODE" VARCHAR2(25 BYTE), 
	"RELEASE_REASON" VARCHAR2(240 BYTE), 
	"STATUS_FLAG" VARCHAR2(25 BYTE), 
	"LAST_UPDATE_LOGIN" NUMBER(15,0), 
	"CREATION_DATE" DATE, 
	"CREATED_BY" NUMBER(15,0), 
	"ATTRIBUTE_CATEGORY" VARCHAR2(150 BYTE), 
	"ATTRIBUTE15" VARCHAR2(150 BYTE), 
	"ORG_ID" NUMBER(15,0) DEFAULT NULL, 
	"RESPONSIBILITY_ID" NUMBER(15,0), 
	"RCV_TRANSACTION_ID" NUMBER, 
	"HOLD_DETAILS" VARCHAR2(2000 BYTE), 
	"LINE_NUMBER" NUMBER, 
	"HOLD_ID" NUMBER(15,0), 
	"WF_STATUS" VARCHAR2(30 BYTE), 
	"VALIDATION_REQUEST_ID" NUMBER(15,0)
   )  ;

CREATE TABLE AP_INVOICES (
  INVOICE_ID                         NUMBER(15)     NOT NULL,
  LAST_UPDATE_DATE                   DATE           NOT NULL,
  LAST_UPDATED_BY                    NUMBER(15)     NOT NULL,
  VENDOR_ID                          NUMBER(15),
  INVOICE_NUM                        VARCHAR2(50)   NOT NULL,
  SET_OF_BOOKS_ID                    NUMBER(15)     NOT NULL,
  INVOICE_CURRENCY_CODE              VARCHAR2(15)   NOT NULL,
  PAYMENT_CURRENCY_CODE              VARCHAR2(15)   NOT NULL,
  PAYMENT_CROSS_RATE                 NUMBER         NOT NULL,
  INVOICE_AMOUNT                     NUMBER,
  VENDOR_SITE_ID                     NUMBER(15),
  AMOUNT_PAID                        NUMBER,
  DISCOUNT_AMOUNT_TAKEN              NUMBER,
  INVOICE_DATE                       DATE,
  SOURCE                             VARCHAR2(25),
  INVOICE_TYPE_LOOKUP_CODE           VARCHAR2(25),
  DESCRIPTION                        VARCHAR2(240),
  BATCH_ID                           NUMBER(15),
  AMOUNT_APPLICABLE_TO_DISCOUNT      NUMBER,
  TAX_AMOUNT                         NUMBER,
  TERMS_ID                           NUMBER(15),
  TERMS_DATE                         DATE,
  PAYMENT_METHOD_LOOKUP_CODE         VARCHAR2(25),
  PAY_GROUP_LOOKUP_CODE              VARCHAR2(30),
  ACCTS_PAY_CODE_COMBINATION_ID      NUMBER(15),
  PAYMENT_STATUS_FLAG                VARCHAR2(1),
  CREATION_DATE                      DATE,
  CREATED_BY                         NUMBER(15),
  BASE_AMOUNT                        NUMBER,
  VAT_CODE                           VARCHAR2(15),
  LAST_UPDATE_LOGIN                  NUMBER(15),
  EXCLUSIVE_PAYMENT_FLAG             VARCHAR2(1),
  PO_HEADER_ID                       NUMBER(15),
  FREIGHT_AMOUNT                     NUMBER,
  GOODS_RECEIVED_DATE                DATE,
  INVOICE_RECEIVED_DATE              DATE,
  VOUCHER_NUM                        VARCHAR2(50),
  APPROVED_AMOUNT                    NUMBER,
  RECURRING_PAYMENT_ID               NUMBER(15),
  EXCHANGE_RATE                      NUMBER,
  EXCHANGE_RATE_TYPE                 VARCHAR2(30),
  EXCHANGE_DATE                      DATE,
  EARLIEST_SETTLEMENT_DATE           DATE,
  ORIGINAL_PREPAYMENT_AMOUNT         NUMBER,
  DOC_SEQUENCE_ID                    NUMBER,
  DOC_SEQUENCE_VALUE                 NUMBER,
  DOC_CATEGORY_CODE                  VARCHAR2(30),
  ATTRIBUTE1                         VARCHAR2(150),
  ATTRIBUTE2                         VARCHAR2(150),
  ATTRIBUTE3                         VARCHAR2(150),
  ATTRIBUTE4                         VARCHAR2(150),
  ATTRIBUTE5                         VARCHAR2(150),
  ATTRIBUTE6                         VARCHAR2(150),
  ATTRIBUTE7                         VARCHAR2(150),
  ATTRIBUTE8                         VARCHAR2(150),
  ATTRIBUTE9                         VARCHAR2(150),
  ATTRIBUTE10                        VARCHAR2(150),
  ATTRIBUTE11                        VARCHAR2(150),
  ATTRIBUTE12                        VARCHAR2(150),
  ATTRIBUTE13                        VARCHAR2(150),
  ATTRIBUTE14                        VARCHAR2(150),
  ATTRIBUTE15                        VARCHAR2(150),
  ATTRIBUTE_CATEGORY                 VARCHAR2(150),
  APPROVAL_STATUS                    VARCHAR2(25),
  APPROVAL_DESCRIPTION               VARCHAR2(240),
  INVOICE_DISTRIBUTION_TOTAL         NUMBER,
  POSTING_STATUS                     VARCHAR2(15),
  PREPAY_FLAG                        VARCHAR2(1),
  AUTHORIZED_BY                      VARCHAR2(25),
  CANCELLED_DATE                     DATE,
  CANCELLED_BY                       NUMBER(15),
  CANCELLED_AMOUNT                   NUMBER,
  TEMP_CANCELLED_AMOUNT              NUMBER,
  PROJECT_ACCOUNTING_CONTEXT         VARCHAR2(30),
  USSGL_TRANSACTION_CODE             VARCHAR2(30),
  USSGL_TRX_CODE_CONTEXT             VARCHAR2(30),
  PROJECT_ID                         NUMBER(15),
  TASK_ID                            NUMBER(15),
  EXPENDITURE_TYPE                   VARCHAR2(30),
  EXPENDITURE_ITEM_DATE              DATE,
  PA_QUANTITY                        NUMBER(22,5),
  EXPENDITURE_ORGANIZATION_ID        NUMBER(15),
  PA_DEFAULT_DIST_CCID               NUMBER(15),
  VENDOR_PREPAY_AMOUNT               NUMBER,
  PAYMENT_AMOUNT_TOTAL               NUMBER,
  AWT_FLAG                           VARCHAR2(1),
  AWT_GROUP_ID                       NUMBER(15),
  REFERENCE_1                        VARCHAR2(30),
  REFERENCE_2                        VARCHAR2(30),
  ORG_ID                             NUMBER(15),
  PRE_WITHHOLDING_AMOUNT             NUMBER,
  GLOBAL_ATTRIBUTE_CATEGORY          VARCHAR2(150),
  GLOBAL_ATTRIBUTE1                  VARCHAR2(150),
  GLOBAL_ATTRIBUTE2                  VARCHAR2(150),
  GLOBAL_ATTRIBUTE3                  VARCHAR2(150),
  GLOBAL_ATTRIBUTE4                  VARCHAR2(150),
  GLOBAL_ATTRIBUTE5                  VARCHAR2(150),
  GLOBAL_ATTRIBUTE6                  VARCHAR2(150),
  GLOBAL_ATTRIBUTE7                  VARCHAR2(150),
  GLOBAL_ATTRIBUTE8                  VARCHAR2(150),
  GLOBAL_ATTRIBUTE9                  VARCHAR2(150),
  GLOBAL_ATTRIBUTE10                 VARCHAR2(150),
  GLOBAL_ATTRIBUTE11                 VARCHAR2(150),
  GLOBAL_ATTRIBUTE12                 VARCHAR2(150),
  GLOBAL_ATTRIBUTE13                 VARCHAR2(150),
  GLOBAL_ATTRIBUTE14                 VARCHAR2(150),
  GLOBAL_ATTRIBUTE15                 VARCHAR2(150),
  GLOBAL_ATTRIBUTE16                 VARCHAR2(150),
  GLOBAL_ATTRIBUTE17                 VARCHAR2(150),
  GLOBAL_ATTRIBUTE18                 VARCHAR2(150),
  GLOBAL_ATTRIBUTE19                 VARCHAR2(150),
  GLOBAL_ATTRIBUTE20                 VARCHAR2(150),
  AUTO_TAX_CALC_FLAG                 VARCHAR2(1),
  PAYMENT_CROSS_RATE_TYPE            VARCHAR2(30),
  PAYMENT_CROSS_RATE_DATE            DATE,
  PAY_CURR_INVOICE_AMOUNT            NUMBER,
  MRC_BASE_AMOUNT                    VARCHAR2(2000),
  MRC_EXCHANGE_RATE                  VARCHAR2(2000),
  MRC_EXCHANGE_RATE_TYPE             VARCHAR2(2000),
  MRC_EXCHANGE_DATE                  VARCHAR2(2000),
  MRC_POSTING_STATUS                 VARCHAR2(2000),
  GL_DATE                            DATE           NOT NULL,
  AWARD_ID                           NUMBER(15),
  PAID_ON_BEHALF_EMPLOYEE_ID         NUMBER(15),
  AMT_DUE_CCARD_COMPANY              NUMBER,
  AMT_DUE_EMPLOYEE                   NUMBER,
  APPROVAL_READY_FLAG                VARCHAR2(1)    NOT NULL,
  APPROVAL_ITERATION                 NUMBER(9),
  WFAPPROVAL_STATUS                  VARCHAR2(50)   NOT NULL,
  REQUESTER_ID                       NUMBER(15),
  VALIDATION_REQUEST_ID              NUMBER(15),
  VALIDATED_TAX_AMOUNT               NUMBER,
  QUICK_CREDIT                       VARCHAR2(1),
  CREDITED_INVOICE_ID                NUMBER(15),
  DISTRIBUTION_SET_ID                NUMBER(15),
  APPLICATION_ID                     NUMBER(15),
  PRODUCT_TABLE                      VARCHAR2(30),
  REFERENCE_KEY1                     VARCHAR2(150),
  REFERENCE_KEY2                     VARCHAR2(150),
  REFERENCE_KEY3                     VARCHAR2(150),
  REFERENCE_KEY4                     VARCHAR2(150),
  REFERENCE_KEY5                     VARCHAR2(150),
  TOTAL_TAX_AMOUNT                   NUMBER,
  SELF_ASSESSED_TAX_AMOUNT           NUMBER,
  TAX_RELATED_INVOICE_ID             NUMBER(15),
  TRX_BUSINESS_CATEGORY              VARCHAR2(240),
  USER_DEFINED_FISC_CLASS            VARCHAR2(240),
  TAXATION_COUNTRY                   VARCHAR2(30),
  DOCUMENT_SUB_TYPE                  VARCHAR2(150),
  SUPPLIER_TAX_INVOICE_NUMBER        VARCHAR2(150),
  SUPPLIER_TAX_INVOICE_DATE          DATE,
  SUPPLIER_TAX_EXCHANGE_RATE         NUMBER,
  TAX_INVOICE_RECORDING_DATE         DATE,
  TAX_INVOICE_INTERNAL_SEQ           VARCHAR2(150),
  LEGAL_ENTITY_ID                    NUMBER(15),
  HISTORICAL_FLAG                    VARCHAR2(1),
  FORCE_REVALIDATION_FLAG            VARCHAR2(1),
  BANK_CHARGE_BEARER                 VARCHAR2(30),
  REMITTANCE_MESSAGE1                VARCHAR2(150),
  REMITTANCE_MESSAGE2                VARCHAR2(150),
  REMITTANCE_MESSAGE3                VARCHAR2(150),
  UNIQUE_REMITTANCE_IDENTIFIER       VARCHAR2(30),
  URI_CHECK_DIGIT                    VARCHAR2(2),
  SETTLEMENT_PRIORITY                VARCHAR2(30),
  PAYMENT_REASON_CODE                VARCHAR2(30),
  PAYMENT_REASON_COMMENTS            VARCHAR2(240),
  PAYMENT_METHOD_CODE                VARCHAR2(30),
  DELIVERY_CHANNEL_CODE              VARCHAR2(30),
  QUICK_PO_HEADER_ID                 NUMBER(15),
  NET_OF_RETAINAGE_FLAG              VARCHAR2(1),
  RELEASE_AMOUNT_NET_OF_TAX          NUMBER,
  CONTROL_AMOUNT                     NUMBER,
  PARTY_ID                           NUMBER(15),
  PARTY_SITE_ID                      NUMBER(15),
  PAY_PROC_TRXN_TYPE_CODE            VARCHAR2(30),
  PAYMENT_FUNCTION                   VARCHAR2(30),
  CUST_REGISTRATION_CODE             VARCHAR2(50),
  CUST_REGISTRATION_NUMBER           VARCHAR2(30),
  PORT_OF_ENTRY_CODE                 VARCHAR2(30),
  EXTERNAL_BANK_ACCOUNT_ID           NUMBER(15),
  VENDOR_CONTACT_ID                  NUMBER(15),
  INTERNAL_CONTACT_EMAIL             VARCHAR2(2000),
  DISC_IS_INV_LESS_TAX_FLAG          VARCHAR2(1),
  EXCLUDE_FREIGHT_FROM_DISCOUNT      VARCHAR2(1),
  PAY_AWT_GROUP_ID                   NUMBER(15),
  ORIGINAL_INVOICE_AMOUNT            NUMBER,
  DISPUTE_REASON                     VARCHAR2(100),
  REMIT_TO_SUPPLIER_NAME             VARCHAR2(240),
  REMIT_TO_SUPPLIER_ID               NUMBER(15),
  REMIT_TO_SUPPLIER_SITE             VARCHAR2(240),
  REMIT_TO_SUPPLIER_SITE_ID          NUMBER(15),
  RELATIONSHIP_ID                    NUMBER(15),
  PO_MATCHED_FLAG                    VARCHAR2(1),
  VALIDATION_WORKER_ID               NUMBER(15),
  CONSTRAINT PK_AP_INVOICES PRIMARY KEY (INVOICE_ID)
);
"""

# AGENT_ENDPOINT_ID=ocid1.genaiagentendpoint.oc1.ap-osaka-1.amaaaaaarykjadqah2zw7mxczrxoa6o3ebdneenum4s5g5mqfk2urommiytq
# MCP_SERVER_PORT=8000
# REGION=ap-osaka-1
# PROFILE=osaka

async def main():
    agent_endpoint_id=os.getenv("AGENT_ENDPOINT_ID")
    region=os.getenv("REGION")
    profile=os.getenv("PROFILE")
    
    client = AgentClient(auth_type="api_key", profile=profile, region=region)

    sql_tool_with_inline_schema = AgenticSqlTool(
        name="get_invoice_holdings",
        description="Use this tool to answer questions about invoice holds.",
        database_schema=InlineInputLocation(content=INLINE_DATABASE_SCHEMA),
        model_size=ModelSize.LARGE,
        dialect=SqlDialect.ORACLE_SQL,
        db_tool_connection_id="ocid1.databasetoolsconnection.oc1.ap-osaka-1.amaaaaaarykjadqa7ni7qmam45tfm55omynvz5sxrakmy25w37nf7mdajfxq",
        enable_sql_execution=True,
        enable_self_correction=True,
        #icl_examples=ObjectStorageInputLocation(namespace_name="namespace", bucket_name="bucket", prefix="_sql.icl_examples.txt"),
        custom_instructions="selected columns : invoice_id, line_location_id, hold_lookup_code, last_update_date, last_updated_by, held_by, hold_date, hold_reason, release_lookup_code, release_reason, org_id, responsibility_id, rcv_transaction_id, hold_details, line_number, hold_id, wf_status, validation_request_id"
    )

    agent = Agent(
        client=client,
        agent_endpoint_id=agent_endpoint_id,
        instructions="Use the tools to answer the questions.",

        tools=[sql_tool_with_inline_schema]
    )

    # 2개의 질문을 차례로 질의하고 답변받음
    # input_msg ="홀딩된 인보이스 목록을 보여줘, hold 이유도 포함하여  20건 만 보여주고 hold_date으로 descending 해줘" 
    input_msg ="list first 10 records in ap_holds_all where release_reason is null " 
    input_msg ="list first 10 records in ap_holds_all where release_reason is null and hold_loook_code in ('QTY ORD', 'QTY  REC', 'PRICE', 'AMT ORG');"
    input_msg =" get invoice holding list first 10 records"
    print(f"Running: {input_msg}")
    response = await agent.run_async(input_msg)
    
    response.pretty_print()
    #print(f"답변: \n{response.messages}")

    # invoice_id: 13193
    #input_msg ="list  first 10 records in ap_holds_all where release_reason is null and invoice_id='13193' " 
    
    input_msg ="list details invoice holding info for invoice_id='81882'  " 
    print(f"Running: {input_msg}")
    response = await agent.run_async(input_msg)
    response.pretty_print()

if __name__ == "__main__":
    asyncio.run(main())