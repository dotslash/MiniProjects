/**
 * Created by ssai on 5/16/14.
 */
package multi.threading;

import org.apache.commons.lang3.tuple.Pair;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Attributes;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.concurrent.*;

public class ElectionResult {

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
    public static void main(String[] args) throws IOException, InterruptedException, ExecutionException {

        long start = System.currentTimeMillis();
        ArrayList<StateWiseDetails> stateWiseDetails = new ArrayList<StateWiseDetails>();
        Document doc = Jsoup.connect("http://eciresults.nic.in/ConstituencywiseS2437.htm?ac=37").get();
        Elements newsHeadlines = doc.select("input");
        int pres = 1;
        for (Element e : newsHeadlines) {
            if (e.id().startsWith("h")) {
                continue;
            }
            Attributes attr = e.attributes();
            String[] val = attr.get("value").split(";");
            String stateCode = getStateCode(pres++);
            ArrayList<Pair<String, String>> constituencies = new ArrayList<Pair<String,String>>();
            for (String value: val) {
                String[] arr = value.trim().split(",");
                Pair<String, String> p = Pair.of(arr[0], arr[1]);
                constituencies.add(p);
            }
            stateWiseDetails.add(new StateWiseDetails(e.id().substring(6), stateCode, constituencies));
        }
        //details of all states are ready


        ExecutorService executorService = Executors.newFixedThreadPool(stateWiseDetails.size());
        ArrayList<Future<String>> results = new ArrayList<Future<String>>();
        for (final StateWiseDetails state : stateWiseDetails) {
             Future<String> submit = executorService.submit(new Callable<String>() {
                @Override
                public String call() throws IOException {
                    System.out.printf("starting thread for %s %s\n", state.name, state.stateCode);
                    String ret = StateWiseDetails.getStateResults(state);
                    System.out.printf("finished thread for %s %s\n", state.name, state.stateCode );
                    return ret;
                }
            });
            results.add(submit);
        }
        executorService.shutdown();
        PrintWriter writer = new PrintWriter(System.getProperty("user.home") + "/electionResult.html", "UTF-8");
        writer.write("<style>\n" +
                "table,th,td\n" +
                "{\n" +
                "border:1px solid black;\n" +
                "border-collapse:collapse;\n" +
                "}\n" +
                "</style>");

        executorService.awaitTermination(1, TimeUnit.DAYS);
        for (Future<String> f : results) {
            writer.write(f.get());
        }
        writer.close();
        System.out.println((System.currentTimeMillis() - start)/1000);
    }

}
