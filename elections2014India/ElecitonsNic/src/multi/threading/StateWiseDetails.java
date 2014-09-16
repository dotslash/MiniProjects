package multi.threading;

import org.apache.commons.lang3.tuple.Pair;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Created by ssai on 5/16/14.
 */
public class StateWiseDetails {
    public final String name;
    public final String stateCode;
    public final List<Pair<String, String>> constituencies;

    public StateWiseDetails(String name, String stateCode, List<Pair<String, String>> constituencies) {
        this.name = name;
        this.stateCode = stateCode;
        this.constituencies = constituencies;
    }

    public static String getStateResults(StateWiseDetails state) throws IOException {
        String begin = String.format("<br><b>%s</b><br>\n<table cellpadding=\"4\">", state.name);
        String end = "</table>\n";
        StringBuilder builder = new StringBuilder();
        builder.append(begin);
        for (Pair<String, String> constituency : state.constituencies) {
            generateConstituencyReport(state.stateCode, constituency, builder);
        }
        builder.append(end);
        return builder.toString();
    }

    private static void generateConstituencyReport(String stateCode, Pair<String, String> split, StringBuilder builder) throws IOException {

        String url = String.format(
                "http://eciresults.nic.in/Constituencywise%s%s.htm?ac=%s",
                stateCode, split.getKey(), split.getKey());
        ArrayList<String> res = getWinnerRunner(url);
        builder.append(String.format("<tr><td><a href = %s>%s</a> </td>",
                url, split.getValue()));
        for (String result : res) {
            builder.append(String.format("<td>%s</td>", result.substring(0, Math.min(result.length(), 30))));
        }
        builder.append("</tr>\n");
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


}
