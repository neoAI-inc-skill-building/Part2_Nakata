from pydantic import BaseModel


class Prompt(BaseModel):
    prompt: str
    japanese_name: str


EXTRACT_DEFINITION_DATA = {
    "recipient_company": Prompt(
        prompt="(String) 帳票に関するサービスを受けた会社。「御中」や「様」などの敬称の直前もしくは"
        "前の行に記載のある企業名。「株式会社」まで。もしくは、敬称をつけられた人が属する企業名。"
        "請求書の場合、発行会社より受領会社が先に書かれていることが多い。"
        "振込口座がある場合、振込先の会社が受領会社であることはほとんどない。",
        japanese_name="受領会社",
    ),
    "issuing_company": Prompt(
        prompt="(String) 帳票を発行した会社。「御中」や「様」などの敬称の直前もしくは前の行に記載のある企業名。"
        "「株式会社」まで含める。請求書では受領会社より後に書かれていることが多い。"
        "振込口座がある場合、振込先の会社が発行会社であることが多い。",
        japanese_name="発行会社",
    ),
    "transaction_date": Prompt(
        prompt="(String) 帳票の発行日または取引日。yyyy/mm/dd形式で抽出すること。"
        "「発行日」「請求日」「取引日」などのラベルの隣に記載されていることが多い。",
        japanese_name="取引日",
    ),
    "amount_sum": Prompt(
        prompt="(Integer) 帳票全体の合計金額。税込の最終的な請求合計額。"
        "カンマ・円記号・通貨単位は除去し、整数のみで抽出すること。"
        "「請求合計額」「合計金額」「お支払合計金額」などのラベルの隣に記載されていることが多い。",
        japanese_name="取引金額(帳票単位)",
    ),
    "slip_number": Prompt(
        prompt="(String) 帳票の伝票番号・請求番号・明細番号。"
        "「請求No.」「伝票番号」「明細No.」などのラベルの隣に記載されていることが多い。"
        "先頭のゼロも含めてそのまま抽出すること。",
        japanese_name="伝票番号",
    ),
    "tax_sum": Prompt(
        prompt="(Integer) 帳票全体の消費税合計額（8%と10%の合算）。"
        "カンマ・円記号は除去し、整数のみで抽出すること。"
        "「消費税合計」「税額合計」などのラベルの隣に記載されていることが多い。",
        japanese_name="消費税(計)",
    ),
    "amount_tax_8_per": Prompt(
        prompt="(Integer) 消費税8%が適用された取引の税込合計金額。"
        "カンマ・円記号は除去し、整数のみで抽出すること。"
        "8%対象の記載がない場合は'-'とすること。",
        japanese_name="取引金額(税込8%)",
    ),
    "amount_tax_10_per": Prompt(
        prompt="(Integer) 消費税10%が適用された取引の税込合計金額。"
        "カンマ・円記号は除去し、整数のみで抽出すること。"
        "10%対象の記載がない場合は'-'とすること。",
        japanese_name="取引金額(税込10%)",
    ),
    "tax_8_per": Prompt(
        prompt="(Integer) 消費税8%の税額。"
        "カンマ・円記号は除去し、整数のみで抽出すること。"
        "8%の消費税の記載がない場合は'-'とすること。",
        japanese_name="消費税(8%)",
    ),
    "tax_10_per": Prompt(
        prompt="(Integer) 消費税10%の税額。"
        "カンマ・円記号は除去し、整数のみで抽出すること。"
        "10%の消費税の記載がない場合は'-'とすること。",
        japanese_name="消費税(10%)",
    ),
    "billing_address": Prompt(
        prompt="(String) 支払先の会社名。帳票の発行会社と同一であることが多い。"
        "振込先として記載されている口座の名義人・会社名を参考にすること。「株式会社」まで含める。",
        japanese_name="支払先",
    ),
    "payment_methods": Prompt(
        prompt="(String) 支払方法。"
        "「支払方法」「支払い方法」「お支払い方法」などのラベルの隣に記載されていることが多い。"
        "「銀行振込」「クレジットカード」「口座振替」などの文字列をそのまま抽出すること。",
        japanese_name="支払方法",
    ),
    "payment_deadline": Prompt(
        prompt="(String) 支払期限・振込期日。yyyy/mm/dd形式で抽出すること。"
        "「お支払期限」「振込期日」「支払期日」などのラベルの隣に記載されていることが多い。",
        japanese_name="支払期日",
    ),
    "final_payment_amount": Prompt(
        prompt="(Integer) 支払金額。カンマ・円記号は除去し、整数のみで抽出すること。"
        "「支払金額」「お支払金額」「支払い金額」などのラベルの隣に記載されていることが多い。"
        "最終的なお支払い金額。税込の合計額と一致することが多い。",
        japanese_name="支払金額",
    ),
    "bank_account": Prompt(
        prompt="(String) 振込先の金融機関名と支店名。「銀行名」と「支店名」を連結して抽出すること。"
        "例：「みずほ三号」のように金融機関名＋支店名の形式で出力すること。"
        "「銀行」「信金」などの語尾は除去すること。",
        japanese_name="振込先口座(金融機関・支店)",
    ),
    "account_number": Prompt(
        prompt="(String) 振込先の口座番号。数字のみで抽出し、ハイフンや空白は除去すること。",
        japanese_name="口座番号",
    ),
    "contract_date": Prompt(
        prompt="(String) 契約締結日または契約開始日。yyyy/mm/dd形式で抽出すること。"
        "記載がない場合は取引日と同一である場合がある。"
        "「契約日」「契約開始日」「契約締結日」などのラベルの隣に記載されていることが多い。",
        japanese_name="契約締結日",
    ),
    "expiration_date_of_a_contract": Prompt(
        prompt="(String) 契約終了日または契約更新日。yyyy/mm/dd形式で抽出すること。記載がない場合は'-'とすること。"
        "「契約更新日」「契約終了日」「契約更新日」などのラベルの隣に記載されていることが多い。",
        japanese_name="契約終了日(契約更新日)",
    ),
    "recipient_company_telephone_number": Prompt(
        prompt="(String) 受領会社の電話番号。ハイフンを除去した数字のみで抽出すること。"
        "受領会社の住所・郵便番号の近くに記載されていることが多い。"
        "記載がない場合は'-'とすること。",
        japanese_name="受領会社電話番号",
    ),
    "recipient_company_postal_code": Prompt(
        prompt="(String) 受領会社の郵便番号。「〒」記号は除去し、ハイフンを含む形式（例：113-0033）で抽出すること。"
        "受領会社名の近くに記載されていることが多い。",
        japanese_name="受領会社郵便番号",
    ),
    "recipient_company_address": Prompt(
        prompt="(String) 受領会社の住所。都道府県から建物名・部屋番号まで含めて抽出すること。"
        "「〒」や郵便番号は含めないこと。スペースは半角スペースにすること。"
        "受領会社名の近くに記載されていることが多い。",
        japanese_name="受領会社住所",
    ),
    "issuing_company_telephone_number": Prompt(
        prompt="(String) 発行会社の電話番号。ハイフンを除去した数字のみで抽出すること。"
        "「TEL」「電話」などのラベルの隣に記載されていることが多い。"
        "記載がない場合は'-'とすること。",
        japanese_name="発行会社電話番号",
    ),
    "issuing_company_postal_code": Prompt(
        prompt="(String) 発行会社の郵便番号。「〒」記号は除去し、ハイフンを含む形式（例：100-0006）で抽出すること。"
        "発行会社名の近くに記載されていることが多い。",
        japanese_name="発行会社郵便番号",
    ),
    "issuing_company_address": Prompt(
        prompt="(String) 発行会社の住所。都道府県から建物名まで含めて抽出すること。"
        "「〒」や郵便番号は含めないこと。スペースは除去すること。"
        "発行会社名の近くに記載されていることが多い。",
        japanese_name="発行会社住所",
    ),
}
