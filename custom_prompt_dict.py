from pydantic import BaseModel


class Prompt(BaseModel):
    prompt: str
    japanese_name: str


EXTRACT_DEFINITION_DATA = {
    "recipient_company": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="受領会社",
    ),
    "issuing_company": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="発行会社",
    ),
    "transaction_date": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="取引日",
    ),
    "amount_sum": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="取引金額(帳票単位)",
    ),
    "slip_number": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="伝票番号",
    ),
    "tax_sum": Prompt(prompt="# TODO: プロンプト作成", japanese_name="消費税(計)"),
    "amount_tax_8_per": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="取引金額(税込8%)",
    ),
    "amount_tax_10_per": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="取引金額(税込10%)",
    ),
    "tax_8_per": Prompt(prompt="# TODO: プロンプト作成", japanese_name="消費税(8%)"),
    "tax_10_per": Prompt(prompt="# TODO: プロンプト作成", japanese_name="消費税(10%)"),
    "billing_address": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="支払先",
    ),
    "payment_methods": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="支払方法",
    ),
    "payment_deadline": Prompt(prompt="# TODO: プロンプト作成", japanese_name="支払期日"),
    "final_payment_amount": Prompt(prompt="# TODO: プロンプト作成", japanese_name="支払金額"),
    "bank_account": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="振込先口座(金融機関・支店)",
    ),
    "account_number": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="口座番号",
    ),
    "contract_date": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="契約締結日",
    ),
    "expiration_date_of_a_contract": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="契約終了日(契約更新日)",
    ),
    "recipient_company_telephone_number": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="受領会社電話番号",
    ),
    "recipient_company_postal_code": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="受領会社郵便番号",
    ),
    "recipient_company_address": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="受領会社住所",
    ),
    "issuing_company_telephone_number": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="発行会社電話番号",
    ),
    "issuing_company_postal_code": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="発行会社郵便番号",
    ),
    "issuing_company_address": Prompt(
        prompt="# TODO: プロンプト作成",
        japanese_name="発行会社住所",
    ),
}
