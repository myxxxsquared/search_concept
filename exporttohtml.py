
import html
import dbconf

def main():
    conn = dbconf.getconn()
    cur = conn.cursor()
    cur.execute('SELECT `concept_id`, `concept_name`,`concept_found`,`concept_detail` FROM `search_concept`;')

    foutput = open('output.html', 'wt', encoding='utf8')

    for concept_id, concept_name, concept_found, concept_detail in iter(cur.fetchone, None):
        if concept_found is None:
            continue
        if concept_found is 0:
            foutput.write(
                '<h1 style="color:red;"> {}: {} 未找到 </h1>\n\n'.format(
                    concept_id,
                    html.escape(concept_name)
                )
            )
        if concept_found is 1:
            concept_detail = concept_detail.replace('<br/>', '\n')
            concept_detail = concept_detail.replace('<br />', '\n')
            concept_detail = concept_detail.replace('<br>', '\n')

            foutput.write(
                '<h1 style="color:green;"> {}: {} </h1>\n\n{}\n\n'.format(
                    concept_id,
                    html.escape(concept_name),
                    html.escape(concept_detail).replace('\n', '<br/>\n')
                )
            )


if __name__ == '__main__':
    main()
