import org.jsoup.Jsoup;
import org.jsoup.nodes.Attributes;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;

/**
 * Created by dotslash on 5/16/14.
 */

public class ElectionResult {
    public static void main(String[] args) throws IOException {
        long start = System.currentTimeMillis();
        PrintWriter writer = new PrintWriter(System.getProperty("user.home") + "/electionResult.html", "UTF-8");
        writer.write("<style>\n" +
                "table,th,td\n" +
                "{\n" +
                "border:1px solid black;\n" +
                "border-collapse:collapse;\n" +
                "}\n" +
                "</style>");
        Document doc = Jsoup.connect("http://eciresults.nic.in/ConstituencywiseS2437.htm?ac=37").get();
        Elements newsHeadlines = doc.select("input");
        int pres = 1;
        for (Element e : newsHeadlines) {
            if (e.id().startsWith("h")) {
                continue;
            }
            writer.write(String.format("<br><b>%s</b><br>\n<table cellpadding=\"4\">", e.id().substring(6)));
            Attributes attr = e.attributes();
            String[] val = attr.get("value").split(";");
            String stateCode = getStateCode(pres++);
            for (String value: val) {
                value = value.trim();
                generateConstituencyReport(stateCode, value.split(","), writer);
            }
            writer.write("</table>\n");

        }
        writer.close();
        System.out.println((System.currentTimeMillis() - start)/1000);
    }
    private static int constNum = 0;
    private static void generateConstituencyReport(String s, String[] split, PrintWriter writer) throws IOException {

        String url = String.format(
                "http://eciresults.nic.in/Constituencywise%s%s.htm?ac=%s",
                s, split[0], split[0]);
        ArrayList<String> res = getWinnerRunner(url);
        writer.write(String.format("<tr><td><a href = %s>%s</a> </td>",
                url, split[1]));
        for (String result : res) {
            writer.write(String.format("<td>%s</td>", result.substring(0, Math.min(result.length(), 30))));
        }
        writer.write("</tr>\n");
        writer.flush();
        System.out.println(constNum++ + " out of 542 constituencies");

    }

    private static ArrayList<String> getWinnerRunner(String url) throws IOException {
        try{
            Document doc = Jsoup.connect(url).get();
            Element div = doc.select("#div1").get(0);
            Elements table = div.getElementsByTag("tbody").get(0).getElementsByTag("tr");
            Element winner = table.get(3);
            Element runner = table.get(4);

            ArrayList<String> wInfo = getCandidateInfo(winner);
            ArrayList<String> rInfo = getCandidateInfo(runner);

            wInfo.addAll(rInfo);
            return wInfo;
        } catch (Exception e){
            e.printStackTrace();
            return new ArrayList<String>();
        }
    }

    private static ArrayList<String> getCandidateInfo(Element contestant) {
        ArrayList<String> ret = new ArrayList<String>();
        Elements allElements = contestant.getAllElements();
        ret.add(allElements.get(1).text());
        ret.add(allElements.get(2).text().replaceAll("[a-z ]", ""));
        ret.add(allElements.get(3).text().substring(0));
        return ret;
    }

    private static String getStateCode(int i) {
        String ret = "S";
        if (i > 28) {
            ret = "U";
            i = i - 28;
        }
        if (i<10) ret += "0";
        ret+=i;
        return ret;
    }
}
